BEGIN;
DROP SCHEMA IF EXISTS http CASCADE;
CREATE SCHEMA http;


CREATE FUNCTION http.get(
    aschema text,
    afunction text,
    environ jsonb,
    apath jsonb,
    args jsonb DEFAULT '{}') RETURNS json AS $$
DECLARE
    body text;
    result json;
BEGIN
    body := format('SELECT array_to_json(array_agg(row_to_json(row, true)), true) '
                   'FROM %I.%I($1, $2, $3) as row;',
                   aschema, 'get_' || afunction);
    EXECUTE body INTO result USING environ, apath, args;
    RETURN result;
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION http.post(
    aschema text,
    afunction text,
    environ jsonb,
    apath jsonb,
    args jsonb DEFAULT '{}',
    request_body bytea DEFAULT '') RETURNS json AS $$
DECLARE
    body text;
    result json;
BEGIN
    body := format('SELECT array_to_json(array_agg(row_to_json(row, true)), true)
                    FROM %I.%I($1, $2, $3, $4) as row;',
                   aschema, 'get_' || afunction);
    EXECUTE body INTO result USING environ, apath, args, request_body;
    RETURN result;
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION http.get_test(jsonb, jsonb, jsonb) 
    RETURNS table(environ jsonb, path jsonb, args jsonb) AS $$
    select $1, $2, $3;
$$ LANGUAGE SQL;


CREATE FUNCTION http.post_test(jsonb, jsonb, jsonb, bytea) 
    RETURNS table(environ jsonb, path jsonb, args jsonb, request bytea) AS $$
    select $1, $2, $3, $4;
$$ LANGUAGE SQL;


CREATE FUNCTION http.get_test_not_found(jsonb, jsonb, jsonb) 
    RETURNS table(environ jsonb, path jsonb, args jsonb) AS $$
DECLARE
BEGIN
    RAISE '404';
    RETURN QUERY SELECT $1, $2, $3;
end;
$$ LANGUAGE plpgsql;

COMMIT;
