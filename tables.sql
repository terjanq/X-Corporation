-- Drop tables
DROP TABLE IF EXISTS "Employee_data" ;
DROP TABLE IF EXISTS "Employee_auth";
DROP TABLE IF EXISTS "Employee_relations";
DROP TABLE IF EXISTS "Employee_root";

DROP FUNCTION IF EXISTS insert_employee(emp_id bigint, emp_superior bigint, emp_password character varying, data character varying);
DROP FUNCTION IF EXISTS remove_employee(emp_id bigint);
DROP FUNCTION IF EXISTS update_po(emp_id bigint, id bigint, inferior_end bigint);

DROP USER IF EXISTS app;


-- Create tables
CREATE TABLE "Employee_auth" (
	"emp_id" bigint NOT NULL UNIQUE,
	"emp_password" varchar(32) NOT NULL,
	CONSTRAINT Employee_auth_pk PRIMARY KEY ("emp_id")
);


CREATE TABLE "Employee_relations" (
	"emp_id" bigint NOT NULL UNIQUE,
	"emp_superior" bigint,
	"id" bigint,
	"inferior_end" bigint,
	CONSTRAINT Employee_relations_pk PRIMARY KEY ("emp_id")
);

CREATE TABLE "Employee_root" (
	"emp_id" bigint NOT NULL UNIQUE,
	CONSTRAINT Employee_root_pk PRIMARY KEY ("emp_id")
);


CREATE TABLE "Employee_data" (
	"emp_id" bigint NOT NULL UNIQUE,
	"emp_data" varchar(100),
	CONSTRAINT Employee_data_pk PRIMARY KEY ("emp_id")
);

-- Add constraints

ALTER TABLE "Employee_auth" ADD CONSTRAINT "Employee_auth_fk0" FOREIGN KEY ("emp_id") REFERENCES "Employee_relations"("emp_id");


ALTER TABLE "Employee_data" ADD CONSTRAINT "Employee_data_fk0" FOREIGN KEY ("emp_id") REFERENCES "Employee_relations"("emp_id");

CREATE INDEX "in_order_idx" ON "Employee_relations" (id);
CREATE INDEX "post_order_idx" ON "Employee_relations" (inferior_end);
CREATE INDEX "emp_superior_idx" ON "Employee_relations" (emp_superior);

--  CREATING FUNCTIONS

CREATE FUNCTION insert_employee(emp_id bigint, emp_superior bigint, emp_password varchar(32), data varchar(100))
RETURNS int AS $$
INSERT INTO "Employee_relations" (emp_id, emp_superior) VALUES($1, $2);
INSERT INTO "Employee_auth" VALUES($1, $3);
INSERT INTO "Employee_data" VALUES($1, $4);

SELECT 1;

$$ LANGUAGE SQL SECURITY DEFINER;

CREATE FUNCTION remove_employee(emp_id bigint)
RETURNS int AS $$
DELETE FROM "Employee_data" WHERE emp_id = $1;
DELETE FROM "Employee_auth" WHERE emp_id = $1;
DELETE FROM "Employee_relations" WHERE emp_id = $1;
SELECT 1;

$$ LANGUAGE SQL SECURITY DEFINER;


CREATE FUNCTION update_po(emp_id bigint, id bigint, inferior_end bigint)
RETURNS int AS $$
	
	UPDATE "Employee_relations" SET id = $2, inferior_end = $3 WHERE emp_id = $1;
	SELECT 1;

$$ LANGUAGE SQL SECURITY DEFINER;


 -- CREATING APP USER


CREATE USER app NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN ENCRYPTED PASSWORD 'qwerty';
GRANT SELECT ON TABLE "Employee_auth" TO app;
GRANT SELECT ON TABLE "Employee_data" TO app;
GRANT SELECT ON TABLE "Employee_root" TO app;
GRANT SELECT ON TABLE "Employee_relations" TO app;
GRANT UPDATE (emp_data) ON TABLE "Employee_data" TO app;
GRANT EXECUTE ON FUNCTION insert_employee(emp_id bigint, emp_superior bigint, emp_password character varying, data character varying) TO app;
GRANT EXECUTE ON FUNCTION remove_employee(emp_id bigint) TO app;
GRANT EXECUTE ON FUNCTION update_po(emp_id bigint, id bigint, inferior_end bigint) TO app;



 -- Inserting test-data

-- SELECT insert_employee(0, -1, 'pass1', 'example data 2');
-- SELECT insert_employee(1, 0, 'pass1', 'example data 2');
-- SELECT insert_employee(3, 1, 'pass1', 'example data 2');
-- SELECT insert_employee(2, 1, 'pass1', 'example data 2');
-- SELECT insert_employee(4, 2, 'pass2', 'example data 2');
-- SELECT insert_employee(5, 3, 'pass2', 'example data 2');



-- SELECT update(0, 0, 5), update(1,1,4), update(3,2,2);

-- SELECT * FROM "Employee_relations";
