BEGIN;
DROP SCHEMA IF EXISTS http CASCADE;
CREATE SCHEMA http;


CREATE FUNCTION http.auth(auser text, apassword text) RETURNS boolean AS $$
    SELECT auser = apassword;
$$ LANGUAGE SQL;


CREATE FUNCTION http.get_test(VARIADIC text[]) RETURNS TABLE(name text, name2 text) AS $$
       select * from unnest($1) as a, unnest($1) as b;
$$ LANGUAGE SQL;


CREATE FUNCTION http.get(aschema text, afunction text, apath text, auser text) RETURNS json AS $$
DECLARE
  args text;
  result json;
BEGIN
    SELECT array_to_string(array_agg(
        (SELECT quote_literal(a[1]) || coalesce('::' || b[2], '')
         FROM regexp_split_to_array(row, E'::') AS a,
              regexp_split_to_array(row, E'::') AS b)
              ), ',')
    FROM unnest(regexp_split_to_array(apath, E'\/')) AS row INTO args;
    args := format('SELECT array_to_json(array_agg(row_to_json(row, true)), true) FROM %I.%I(%L, %s) as row;', aschema, 'get_' || afunction, auser, args);
    RAISE NOTICE '%', args;
    EXECUTE args into result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
COMMIT;
