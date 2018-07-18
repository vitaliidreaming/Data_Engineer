
# TASK 3
### SQL query to find the most recent version of each app.

**a)** SQL code for creating the following table **apps** :

pk | id | title | rating | last_update_date
- |- |- | - |-
1 | com.facebook.katana | Facebook | 4.0 | 2016-09-12
2 | com.whatsapp | WhatsApp | 4.5 | 2016-09-11
3 | com.whatsapp | WhatsApp | 4.4 | 2016-09-12
4 | com.nianticlabs.pokemongo | Pokémon GO | 4.6 | 2016-09-05
5 | com.nianticlabs.pokemongo | Pokémon GO | 4.3 | 2016-09-06
6 | com.nianticlabs.pokemongo | Pokémon GO | 4.1 | 2016-09-07

> _Uncomment first line to **delete** previously created table by this query!_

```SQL
--DROP TABLE apps; -- to reuse the query without an error.

-- the SQL code for creating the following table:
CREATE TABLE apps
(
	pk serial PRIMARY KEY,
    id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
	rating NUMERIC(2, 1) NOT NULL,
	last_update_date DATE NOT NULL DEFAULT CURRENT_DATE
);
```

> _because the **pk** column auto-increments, have no need (and in this realization right) to specify the **pk** column._

```SQL
-- Adding values to the Table: 
INSERT INTO apps (id, title, rating, last_update_date)
VALUES 
('com.facebook.katana', 'Facebook', 4.0, '2016-09-12'),
('com.whatsapp', 'WhatsApp', 4.5, '2016-09-11'),
('com.whatsapp', 'WhatsApp', 4.4, '2016-09-12'),
('com.nianticlabs.pokemongo', 'Pokémon GO', 4.6, '2016-09-05'),
('com.nianticlabs.pokemongo', 'Pokémon GO', 4.3, '2016-09-06'),
('com.nianticlabs.pokemongo', 'Pokémon GO', 4.1, '2016-09-07');
```

**b)** SQL query for finding the most recent version of each app.

```SQL
-- Finding the most recent version of each app.
-- Wrote 'Select' and 'Join' statements a bit more explicit to ensure absence of duplicates.
SELECT t.pk, t.id, t.title, t.rating, t.last_update_date
FROM apps t
INNER JOIN ( 
SELECT MAX(pk) max_pk, id, title, MAX(last_update_date) max_last_update_date
FROM apps
GROUP BY id, title) tm
ON t.pk = max_pk and t.title = tm.title and t.last_update_date = max_last_update_date
```



> _the same Query. if we sure that table is not damaged (who knows). **pk** column would point to the most recent version of each app by itself._

```SQL
-- Finding the most recent version of each app. (SIMPLIFIED)
SELECT t.pk, t.id, t.title, t.rating, t.last_update_date
FROM apps t
INNER JOIN ( 
SELECT MAX(pk) max_pk, title,
FROM apps
GROUP BY id, title) tm
ON t.pk = max_pk and t.title = tm.title
```

