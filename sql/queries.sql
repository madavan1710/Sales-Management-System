-- From this Basic Quires starts

SELECT * FROM branches;

SELECT * FROM customer_sales;

SELECT * FROM users;

SELECT * FROM payment_splits;

SELECT * 
FROM customer_sales
WHERE status='Open';

-- From this Aggregation Quires starts

SELECT
SUM(gross_sales) AS total_gross_sales
FROM customer_sales;

SELECT
SUM(received_amount) AS total_received
FROM customer_sales;

SELECT
SUM(pending_amount) AS total_pending
FROM customer_sales;

SELECT
AVG(gross_sales) AS average_sales
FROM customer_sales;

-- From this Join Quires starts

SELECT
cs.sale_id,
b.branch_name,
cs.name,
cs.product_name,
cs.gross_sales

FROM customer_sales cs

JOIN branches b
ON cs.branch_id=b.branch_id;

SELECT
cs.sale_id,
cs.name,
ps.amount_paid,
ps.payment_method

FROM customer_sales cs

JOIN payment_splits ps
ON cs.sale_id=ps.sale_id;

SELECT
b.branch_name,
SUM(cs.gross_sales) AS total_sales

FROM branches b

JOIN customer_sales cs
ON b.branch_id=cs.branch_id

GROUP BY b.branch_name;

SELECT
cs.sale_id,
cs.name AS customer_name,
cs.product_name,
ps.payment_method,
ps.amount_paid

FROM customer_sales cs

JOIN payment_splits ps
ON cs.sale_id = ps.sale_id;

--From this Financial Quires starts

SELECT *
FROM customer_sales
WHERE pending_amount > 5000;

SELECT *
FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;

SELECT
b.branch_name,
SUM(cs.gross_sales) AS total_sales

FROM branches b

JOIN customer_sales cs
ON b.branch_id = cs.branch_id

GROUP BY b.branch_name

ORDER BY total_sales DESC

LIMIT 1;

SELECT
sale_id,
gross_sales,
received_amount,
pending_amount

FROM customer_sales
WHERE sale_id = 1;
