BEGIN;
DROP SCHEMA IF EXISTS http CASCADE;
CREATE SCHEMA http;

CREATE TABLE http.user (
    name text primary key,
    password text,
    created timestamp default (now() at time zone 'utc')
);

INSERT INTO http.user VALUES ('michel', crypt('enzothedog', gen_salt('bf', 10)));

CREATE FUNCTION http.auth_user(
    ausername text,
    apassword text) RETURNS bool AS $$
    select crypt(apassword, password) = password from http.user where name = ausername;
$$ LANGUAGE SQL;


CREATE FUNCTION http.process_request(
    amethod text,
    aschema text,
    afunction text,
    environ jsonb,
    apath jsonb,
    args jsonb DEFAULT '{}',
    request_data bytea DEFAULT null) RETURNS json AS $$
DECLARE
    body text;
    result json;
BEGIN
    body := format('SELECT array_to_json(array_agg(row_to_json(row, true)), true) '
                   'FROM %I.%I($1, $2, $3, $4) as row;',
                   aschema, lower(amethod) || '_' || afunction);
    EXECUTE body INTO result USING environ, apath, args, request_data;
    RETURN result;
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION http.get_test(jsonb, jsonb, jsonb, bytea)
    RETURNS table(environ jsonb, path jsonb, args jsonb) AS $$
    select $1, $2, $3;
$$ LANGUAGE SQL;


CREATE FUNCTION http.post_test(jsonb, jsonb, jsonb, bytea)
    RETURNS table(environ jsonb, path jsonb, args jsonb, request bytea) AS $$
    select $1, $2, $3, $4;
$$ LANGUAGE SQL;


CREATE FUNCTION http.get_test_not_found(jsonb, jsonb, jsonb, bytea)
    RETURNS table(environ jsonb, path jsonb, args jsonb) AS $$
DECLARE
BEGIN
    RAISE '404';
    RETURN QUERY SELECT $1, $2, $3;
end;
$$ LANGUAGE plpgsql;

COMMIT;
