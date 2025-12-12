-- Create the main employees table if it doesn't exist
-- This SQL will be executed by the CI/CD pipeline

CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.{table_id}` (
  id INT64 NOT NULL,
  name STRING NOT NULL,
  email STRING NOT NULL,
  department STRING,
  salary INT64,
  hire_date DATE,
  is_active BOOL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Employee data table - managed by CI/CD pipeline"
);

-- Create a summary table for analytics
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.department_summary` (
  department STRING,
  employee_count INT64,
  avg_salary FLOAT64,
  total_salary INT64,
  last_updated TIMESTAMP
)
OPTIONS(
  description="Department summary statistics"
);
