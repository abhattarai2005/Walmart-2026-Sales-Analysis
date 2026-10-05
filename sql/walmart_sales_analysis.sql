-- Walmart FY2024-FY2026 Sales Analysis
-- SQL analysis of sales and e-commerce performance

USE walmart_sales_analysis;


-- Check the imported data before starting the analysis
SELECT *
FROM walmart_sales
ORDER BY fiscal_year, segment;


-- Make sure all expected records were imported
SELECT COUNT(*) AS total_rows
FROM walmart_sales;


-- Total sales and e-commerce sales for each fiscal year
SELECT
    fiscal_year,
    ROUND(SUM(net_sales_millions) / 1000, 2) AS total_sales_billions,
    ROUND(SUM(ecommerce_sales_millions) / 1000, 2) AS ecommerce_sales_billions
FROM walmart_sales
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Compare the size of each business segment in FY2026
SELECT
    segment,
    ROUND(net_sales_millions / 1000, 2) AS net_sales_billions,
    ROUND(ecommerce_sales_millions / 1000, 2) AS ecommerce_sales_billions
FROM walmart_sales
WHERE fiscal_year = 2026
ORDER BY net_sales_millions DESC;


-- Calculate e-commerce as a percentage of each segment's sales
SELECT
    fiscal_year,
    segment,
    ROUND(net_sales_millions / 1000, 2) AS net_sales_billions,
    ROUND(ecommerce_sales_millions / 1000, 2) AS ecommerce_sales_billions,
    ROUND(
        ecommerce_sales_millions / net_sales_millions * 100,
        2
    ) AS ecommerce_share_percent
FROM walmart_sales
ORDER BY fiscal_year, ecommerce_share_percent DESC;


-- Find each segment's contribution to FY2026 sales
SELECT
    segment,
    ROUND(net_sales_millions / 1000, 2) AS net_sales_billions,
    ROUND(
        net_sales_millions /
        SUM(net_sales_millions) OVER () * 100,
        2
    ) AS sales_share_percent
FROM walmart_sales
WHERE fiscal_year = 2026
ORDER BY sales_share_percent DESC;


-- Compare each year with the previous year using a window function
WITH sales_growth AS (
    SELECT
        fiscal_year,
        segment,
        net_sales_millions,
        LAG(net_sales_millions) OVER (
            PARTITION BY segment
            ORDER BY fiscal_year
        ) AS previous_year_sales
    FROM walmart_sales
)

SELECT
    fiscal_year,
    segment,
    ROUND(net_sales_millions / 1000, 2) AS sales_billions,
    ROUND(previous_year_sales / 1000, 2) AS previous_year_sales_billions,
    ROUND(
        (net_sales_millions - previous_year_sales)
        / previous_year_sales * 100,
        2
    ) AS yoy_growth_percent
FROM sales_growth
WHERE previous_year_sales IS NOT NULL
ORDER BY fiscal_year, yoy_growth_percent DESC;


-- Do the same analysis for e-commerce growth
WITH ecommerce_growth AS (
    SELECT
        fiscal_year,
        segment,
        ecommerce_sales_millions,
        LAG(ecommerce_sales_millions) OVER (
            PARTITION BY segment
            ORDER BY fiscal_year
        ) AS previous_year_ecommerce
    FROM walmart_sales
)

SELECT
    fiscal_year,
    segment,
    ROUND(
        ecommerce_sales_millions / 1000,
        2
    ) AS ecommerce_sales_billions,
    ROUND(
        (
            ecommerce_sales_millions
            - previous_year_ecommerce
        )
        / previous_year_ecommerce * 100,
        2
    ) AS ecommerce_growth_percent
FROM ecommerce_growth
WHERE previous_year_ecommerce IS NOT NULL
ORDER BY fiscal_year, ecommerce_growth_percent DESC;


-- Compare FY2024 directly with FY2026
SELECT
    newer.segment,

    ROUND(
        older.net_sales_millions / 1000,
        2
    ) AS fy2024_sales_billions,

    ROUND(
        newer.net_sales_millions / 1000,
        2
    ) AS fy2026_sales_billions,

    ROUND(
        (
            newer.net_sales_millions
            - older.net_sales_millions
        ) / 1000,
        2
    ) AS sales_added_billions,

    ROUND(
        (
            newer.net_sales_millions
            - older.net_sales_millions
        )
        / older.net_sales_millions * 100,
        2
    ) AS growth_percent

FROM walmart_sales AS newer

JOIN walmart_sales AS older
    ON newer.segment = older.segment

WHERE newer.fiscal_year = 2026
  AND older.fiscal_year = 2024

ORDER BY sales_added_billions DESC;


-- Rank the FY2026 segments from largest to smallest
SELECT
    segment,
    ROUND(net_sales_millions / 1000, 2) AS net_sales_billions,

    RANK() OVER (
        ORDER BY net_sales_millions DESC
    ) AS sales_rank

FROM walmart_sales

WHERE fiscal_year = 2026

ORDER BY sales_rank;