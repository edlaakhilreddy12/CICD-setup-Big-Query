-- SQL transformations to run after data load
-- This creates/updates summary tables

-- Update department summary statistics
CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.department_summary` AS
SELECT 
  department,
  COUNT(*) as employee_count,
  ROUND(AVG(salary), 2) as avg_salary,
  SUM(salary) as total_salary,
  CURRENT_TIMESTAMP() as last_updated
FROM 
  `{project_id}.{dataset_id}.{table_id}`
WHERE 
  is_active = TRUE
GROUP BY 
  department
ORDER BY 
  total_salary DESC;

-- You can add more transformations here
-- Example: Create a view for high earners
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.high_earners` AS
SELECT 
  name,
  email,
  department,
  salary,
  hire_date
FROM 
  `{project_id}.{dataset_id}.{table_id}`
WHERE 
  salary > 90000
  AND is_active = TRUE
ORDER BY 
  salary DESC;
