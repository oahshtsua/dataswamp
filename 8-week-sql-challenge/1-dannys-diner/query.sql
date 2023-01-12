-- Case Study #1: DANNY'S DINER --

SET search_path = dannys_diner;

SELECT * FROM sales;
SELECT * FROM members;
SELECT * FROM menu;

-- 1. What is the total amount each customer spent at the restaurant?
SELECT
  sales.customer_id,
  SUM(menu.price) AS total_amount
FROM sales
JOIN menu
  ON sales.product_id = menu.product_id
GROUP BY sales.customer_id;

-- 2. How many days has each customer visited the restaurant?
SELECT
  customer_id,
  COUNT(DISTINCT order_date) AS visit_count
FROM sales
GROUP BY customer_id;

-- 3. What was the first item from the menu purchased by each customer?
WITH ranked_sales AS (
  SELECT
    customer_id,
    order_date,
    product_name,
    RANK() over (
      PARTITION BY customer_id
      ORDER BY order_date
    ) AS rank
  FROM sales
  JOIN menu
  ON sales.product_id = menu.product_id
)
SELECT
  customer_id,
  product_name
FROM ranked_sales
WHERE rank=1
GROUP BY customer_id, product_name;

-- 4. What is the most purchased item on the menu and how many times was it purchased by all customers?
SELECT
  product_name,
  COUNT(*) AS purchase_count
FROM sales
JOIN menu
  ON sales.product_id = menu.product_id
GROUP BY product_name
ORDER BY purchase_count DESC
FETCH FIRST ROW ONLY;

-- 5. Which item was the most popular for each customer?
WITH favourite_items AS (
  SELECT
    customer_id,
    product_name,
    COUNT(*) AS purchase_count,
    RANK() OVER(
      PARTITION BY customer_id
      ORDER BY COUNT(*) DESC
    )
  FROM sales
  JOIN menu
    ON sales.product_id = menu.product_id
  GROUP BY customer_id, product_name
)
SELECT
  customer_id,
  product_name
FROM favourite_items
WHERE rank=1;

-- 6. Which item was purchased first by the customer after they became a member?
WITH ranked_sales AS (
  SELECT
    sales.customer_id,
    sales.order_date,
    sales.product_id,
    members.join_date,
    RANK() OVER(
      PARTITION BY sales.customer_id
      ORDER BY sales.order_date
    )
  FROM sales
  JOIN members
    ON sales.customer_id = members.customer_id
  WHERE sales.order_date >= members.join_date
)
SELECT
  ranked_sales.customer_id,
  menu.product_name
FROM ranked_sales
JOIN menu
  ON ranked_sales.product_id = menu.product_id
WHERE rank=1
ORDER BY customer_id;

-- 7. Which item was purchased just before the customer became a member?
WITH ranked_sales AS (
  SELECT
    sales.customer_id,
    sales.order_date,
    sales.product_id,
    members.join_date,
    RANK() OVER(
      PARTITION BY sales.customer_id
      ORDER BY sales.order_date DESC
    )
  FROM sales
  JOIN members
    ON sales.customer_id = members.customer_id
  WHERE sales.order_date < members.join_date
)
SELECT
  ranked_sales.customer_id,
  menu.product_name
FROM ranked_sales
JOIN menu
  ON ranked_sales.product_id = menu.product_id
WHERE rank=1
ORDER BY customer_id;

-- 8. What is the total items and amount spent for each member before they became a member?
SELECT
  sales.customer_id,
  COUNT(*) AS total_items,
  SUM(price) AS total_amount
FROM sales
JOIN members
  ON sales.customer_id = members.customer_id
JOIN menu
  ON sales.product_id = menu.product_id
WHERE sales.order_date < members.join_date
GROUP BY sales.customer_id;
ORDER BY customer_id;

-- 9.  If each $1 spent equates to 10 points and sushi has a 2x points multiplier - how many points would each customer have?
WITH order_points AS (
    SELECT
      sales.customer_id,
      sales.product_id,
      menu.product_name,
      menu.price,
    CASE
      WHEN menu.product_name = 'sushi' THEN price * 10 * 2
      ELSE price * 10
    END AS points
  FROM sales
  JOIN menu
    ON sales.product_id = menu.product_id
  )
SELECT
  customer_id,
  sum (points) as total_points
FROM order_points
GROUP BY customer_id
ORDER BY customer_id;

-- 10. In the first week after a customer joins the program (including their join date) they earn 2x points on all items, not just sushi - how many points do customer A and B have at the end of January?
SELECT
  sales.customer_id,
  SUM (
    CASE
      WHEN sales.order_date BETWEEN members.join_date
        AND (members.join_date + 6)
        THEN 2 * menu.price * 10
      WHEN menu.product_name = 'sushi' THEN 2 * menu.price * 10
      ELSE menu.price * 10
    END
  ) AS points
FROM sales
JOIN members
  ON sales.customer_id = members.customer_id
JOIN menu
  ON sales.product_id = menu.product_id
WHERE sales.order_date < '2021-02-01'
GROUP BY sales.customer_id;

-- Bonus Questions --
-- Join All The Things
SELECT
  sales.customer_id,
  sales.order_date,
  menu.product_name,
  menu.price,
  CASE
    WHEN sales.order_date >= members.join_date THEN 'Y'
    ELSE 'N'
  END AS member
FROM sales
JOIN menu
  ON sales.product_id = menu.product_id
LEFT JOIN members
  ON sales.customer_id = members.customer_id
ORDER BY sales.customer_id, sales.order_date, menu.price DESC;

-- Rank All The Things
WITH aggregated_records AS (
  SELECT
    sales.customer_id,
    sales.order_date,
    menu.product_name,
    menu.price,
    CASE
      WHEN sales.order_date >= members.join_date THEN 'Y'
      ELSE 'N'
    END AS member
  FROM sales
  JOIN menu
    ON sales.product_id = menu.product_id
  LEFT JOIN members
    ON sales.customer_id = members.customer_id
)
SELECT
  *,
  CASE
    WHEN member ='N' THEN NULL
    ELSE
      RANK() OVER(
        PARTITION BY customer_id, member
        ORDER BY order_date
      )
  END AS ranking
FROM aggregated_records;
