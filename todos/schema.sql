DROP TABLE if EXISTS todos_todo;
CREATE TABLE "todos_todo" (
    "id" integer NOT NULL PRIMARY KEY,
    "title" varchar(100) NOT NULL CHECK("title" <> ""),
    "pub_date" datetime NOT NULL,
    "closed" bool NOT NULL
)
;
