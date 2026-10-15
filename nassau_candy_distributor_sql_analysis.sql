CREATE DATABASE nassau_candy;
use nassau_candy;
DROP TABLE IF EXISTS nassau_candy_data;
SELECT * FROM nassau_candy_data;
SELECT COUNT(*) AS Total_Rows
FROM nassau_candy_data;
SELECT * FROM nassau_candy_data
LIMIT 10;
SELECT
    SUM(Sales) AS Total_Sales,
    SUM(Cost) AS Total_Cost,
    SUM('Gross Profit') AS Total_Gross_Profit,
    SUM(Units) AS Total_Units,
    COUNT(DISTINCT 'Order ID') AS Total_Orders,
    AVG('Shipping Days') AS Average_Shipping_Days
FROM nassau_candy_data;
DESCRIBE nassau_candy_data;
SELECT
    `Order ID`,
    `Gross Profit`,
    `Shipping Days`
FROM nassau_candy_data
LIMIT 10;
SELECT
    COUNT(DISTINCT `Order ID`) AS Unique_Orders,
    COUNT(`Gross Profit`) AS Gross_Profit_Values,
    COUNT(`Shipping Days`) AS Shipping_Days_Values,
    MIN(`Gross Profit`) AS Min_Profit,
    MAX(`Gross Profit`) AS Max_Profit,
    MIN(`Shipping Days`) AS Min_Shipping_Days,
    MAX(`Shipping Days`) AS Max_Shipping_Days
FROM nassau_candy_data;
SELECT
    SUM(Sales) AS Total_Sales,
    SUM(Cost) AS Total_Cost,
    SUM(`Gross Profit`) AS Total_Gross_Profit,
    SUM(Units) AS Total_Units,
    COUNT(DISTINCT `Order ID`) AS Total_Orders,
    AVG(`Shipping Days`) AS Average_Shipping_Days
FROM nassau_candy_data;

SELECT
    Region,
    COUNT(DISTINCT `Order ID`) AS Total_Orders,
    SUM(Sales) AS Total_Sales,
    SUM(`Gross Profit`) AS Total_Profit,
    SUM(Units) AS Total_Units
FROM nassau_candy_data
GROUP BY Region
ORDER BY Total_Sales DESC;

SELECT
    Region,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    ROUND(
        (SUM(`Gross Profit`) / SUM(Sales)) * 100,
        2
    ) AS Profit_Margin_Percent
FROM nassau_candy_data
GROUP BY Region
ORDER BY Profit_Margin_Percent DESC;

SELECT
    Division,
    COUNT(DISTINCT `Order ID`) AS Total_Orders,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    SUM(Units) AS Total_Units
FROM nassau_candy_data
GROUP BY Division
ORDER BY Total_Sales DESC;

SELECT
    Division,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    ROUND(
        (SUM(`Gross Profit`) / SUM(Sales)) * 100,
        2
    ) AS Profit_Margin_Percent
FROM nassau_candy_data
GROUP BY Division
ORDER BY Profit_Margin_Percent DESC;

SELECT
    `Product Name`,
    COUNT(DISTINCT `Order ID`) AS Total_Orders,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    SUM(Units) AS Total_Units
FROM nassau_candy_data
GROUP BY `Product Name`
ORDER BY Total_Sales DESC
LIMIT 10;

SELECT
    `Product Name`,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    ROUND(
        (SUM(`Gross Profit`) / SUM(Sales)) * 100,
        2
    ) AS Profit_Margin_Percent
FROM nassau_candy_data
GROUP BY `Product Name`
HAVING SUM(Sales) > 500
   AND (SUM(`Gross Profit`) / SUM(Sales)) * 100 < 60
ORDER BY Total_Sales DESC;

SELECT 
    `Product Name`, 
    SUM(Units) AS Total_Units, 
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    ROUND(SUM(`Gross Profit`) / SUM(Units), 2) AS Profit_Per_Unit
FROM nassau_candy_data
GROUP BY `Product Name`
ORDER BY Profit_Per_Unit ASC
LIMIT 10;

SELECT
    `Order ID`,
    `Product Name`,
    Region,
    `Ship Mode`,
    `Shipping Days`,
    Sales,
    `Gross Profit`
FROM nassau_candy_data
WHERE `Shipping Days` > 1800
ORDER BY `Shipping Days` DESC;
SELECT
    Region,
    COUNT(DISTINCT `Order ID`) AS High_Shipping_Orders,
    ROUND(AVG(`Shipping Days`), 2) AS Avg_Shipping_Days,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit
FROM nassau_candy_data
WHERE `Shipping Days` > 1800
GROUP BY Region
ORDER BY High_Shipping_Orders DESC;

SELECT
    `Customer ID`,
    COUNT(DISTINCT `Order ID`) AS Total_Orders,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit
FROM nassau_candy_data
GROUP BY `Customer ID`
ORDER BY Total_Sales DESC
LIMIT 10;

SELECT
    `Product Name`,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit
FROM nassau_candy_data
GROUP BY `Product Name`
HAVING SUM(Sales) > (
    SELECT AVG(Product_Sales)
    FROM (
        SELECT SUM(Sales) AS Product_Sales
        FROM nassau_candy_data
        GROUP BY `Product Name`
    ) AS product_summary
)
ORDER BY Total_Sales DESC;

SELECT
    `Customer ID`,
    COUNT(DISTINCT `Order ID`) AS Total_Orders,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    ROUND(
        (SUM(`Gross Profit`) / SUM(Sales)) * 100,
        2
    ) AS Profit_Margin_Percent
FROM nassau_candy_data
GROUP BY `Customer ID`
HAVING SUM(Sales) > 200
   AND (SUM(`Gross Profit`) / SUM(Sales)) * 100 < 60
ORDER BY Total_Sales DESC;

SELECT
    `Ship Mode`,
    COUNT(*) AS Total_Records,
    SUM(CASE 
            WHEN `Shipping Days` > 1800 THEN 1 
            ELSE 0 
        END) AS High_Shipping_Records,
    ROUND(
        SUM(CASE 
                WHEN `Shipping Days` > 1800 THEN 1 
                ELSE 0 
            END) / COUNT(*) * 100,
        2
    ) AS High_Shipping_Percentage
FROM nassau_candy_data
GROUP BY `Ship Mode`
ORDER BY High_Shipping_Percentage DESC;

SELECT
    `Product Name`,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    ROUND(
        (SUM(`Gross Profit`) / SUM(Sales)) * 100,
        2
    ) AS Profit_Margin,
    CASE
        WHEN (SUM(`Gross Profit`) / SUM(Sales)) * 100 < 50
            THEN 'Low Margin'
        WHEN (SUM(`Gross Profit`) / SUM(Sales)) * 100 < 65
            THEN 'Medium Margin'
        ELSE 'High Margin'
    END AS Margin_Category
FROM nassau_candy_data
GROUP BY `Product Name`
ORDER BY Profit_Margin ASC;

WITH product_metrics AS (
    SELECT
        `Product Name`,
        SUM(Sales) AS Total_Sales,
        SUM(`Gross Profit`) AS Total_Profit,
        (SUM(`Gross Profit`) / SUM(Sales)) * 100 AS Profit_Margin
    FROM nassau_candy_data
    GROUP BY `Product Name`
)

SELECT
    `Product Name`,
    ROUND(Total_Sales, 2) AS Total_Sales,
    ROUND(Total_Profit, 2) AS Total_Profit,
    ROUND(Profit_Margin, 2) AS Profit_Margin
FROM product_metrics
WHERE Profit_Margin >= 65
  AND Total_Sales > 500
ORDER BY Profit_Margin DESC;

CREATE VIEW product_profitability AS
SELECT
    `Product Name`,
    SUM(Units) AS Total_Units,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(`Gross Profit`), 2) AS Total_Profit,
    ROUND(
        (SUM(`Gross Profit`) / SUM(Sales)) * 100,
        2
    ) AS Profit_Margin_Percent,
    ROUND(
        SUM(`Gross Profit`) / SUM(Units),
        2
    ) AS Profit_Per_Unit
FROM nassau_candy_data
GROUP BY `Product Name`;
SELECT *
FROM product_profitability;