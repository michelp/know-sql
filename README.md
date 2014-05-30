know-sql
========

There is a [Postgres wiki page](https://wiki.postgresql.org/wiki/HTTP_API)
describing a possible HTTP API for postgres.  Without having to wait for that, it is
possible to use nginx as a very simple yet powerful HTTP API frontend for
postgres. 

nginx
=====

Using the [ngx_postgres](https://github.com/FRiCKLE/ngx_postgres/)
module that comes with [openresty](https://github.com/openresty)
allows nginx to talk directly to postgres.  Using the following rule,
URL patterns are broken down into function arguments that call into a
postgres dispatch function called 'HTTP_GET':

    http {
        upstream fed {
            postgres_server  127.0.0.1 dbname=fed user=postgres password=postgres;
        }
        server {
            listen 80;
            server_name  politips.us;

            location = / {
                root   html;
                index  index.html index.htm;
            }

            location ~ "/(?<db>\w+)/(?<schema>\w+)/(?<function>\w+)(?<path>/.*){0,}$" {
                rds_json        on;
                postgres_pass   $db;
                postgres_escape $user $remote_user;
                postgres_escape $pass $remote_passwd;
                postgres_query  HEAD GET "SELECT * FROM $schema.HTTP_GET('$function', '$path', '$user', '$pass')";
            }
            error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   html;
            }
        }
    }

The key to the trick is the location regular expression.  It maps URL
elements to access functions in a schema in the database.  These URLs
would generate the following calls:

    /products/api/total_products
    SELECT * FROM api.HTTP_GET('total_products', '', <user>, <pass>);

    /products/api/get_total_products/
    SELECT * FROM api.HTTP_GET('total_products', '/', <user>, <pass>);

    /products/api/get_total_products/2014
    SELECT * FROM api.HTTP_GET('total_products', '/2014', <user>, <pass>);

    /products/api/get_total_products/2014/05
    SELECT * FROM api.HTTP_GET('total_products', '/2014/05', <user>, <pass>);

postgres
========

The HTTP_GET function:

  - Queries the current schema looking for a function named 'get_total_products'

  - Parses the path "/2014/5" into the array '{2014, 5}'

  - Queries the function's signature and generates the correct type casts

  - Authenticates the user, sets the current session's role

  - EXECUTE 'SELECT * FROM api.get_total_products('2014'::int, '5'::int);'

Example here would be a possible implementation of
'get_total_products':

    CREATE FUNCTION api.get_total_products(int, int) returns json AS $$
        SELECT id, sum(amount) as total FROM products WHERE year = $1 and month = $2 GROUP BY id ORDER BY total desc;
    $$ LANGUAGE SQL;

Would return JSON like the following:

      [{id=1, total=42}, {id=... }, ... ]

Postgres functions can be written in [many language](http://www.postgresql.org/docs/devel/static/external-pl.html)
including [Javascript](https://code.google.com/p/plv8js/wiki/PLV8).