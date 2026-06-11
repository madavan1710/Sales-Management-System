--Creating trigger
CREATE OR REPLACE FUNCTION update_received_amount_function()
RETURNS TRIGGER AS $$

DECLARE
    total_received DECIMAL(12,2);

BEGIN

    SELECT COALESCE(SUM(amount_paid),0)
    INTO total_received
    FROM payment_splits
    WHERE sale_id = COALESCE(NEW.sale_id, OLD.sale_id);

    UPDATE customer_sales
    SET
        received_amount = total_received,
        status = CASE
                    WHEN gross_sales - total_received <= 0
                    THEN 'Close'
                    ELSE 'Open'
                 END
    WHERE sale_id = COALESCE(NEW.sale_id, OLD.sale_id);

    RETURN NULL;

END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER update_received_amount_trigger

AFTER INSERT OR UPDATE OR DELETE
ON payment_splits

FOR EACH ROW

EXECUTE FUNCTION update_received_amount_function();

SELECT trigger_name
FROM information_schema.triggers
WHERE event_object_table = 'payment_splits';

UPDATE customer_sales cs
SET received_amount = (
    SELECT COALESCE(SUM(ps.amount_paid),0)
    FROM payment_splits ps
    WHERE ps.sale_id = cs.sale_id
);

UPDATE customer_sales
SET status =
CASE
    WHEN pending_amount <= 0 THEN 'Close'
    ELSE 'Open'
END;

SELECT
sale_id,
gross_sales,
received_amount,
pending_amount

FROM customer_sales;

-- Inserting data into payment splits table for verification
INSERT INTO payment_splits
(sale_id, payment_date, amount_paid, payment_method)

VALUES
(1, '2024-01-20', 5000, 'UPI');

select count(*) from payment_splits;

-- there was an error clarified by Vignesh
SELECT setval(
    pg_get_serial_sequence('payment_splits', 'payment_id'),
    (SELECT MAX(payment_id) FROM payment_splits)
);
