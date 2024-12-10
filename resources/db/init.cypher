CREATE (pc:PublicContext {
  datasets: '[
    {
        "id": "adult",
        "name": "Adult Census Income Dataset",
        "size": 4.8,
        "rows": 48842,
        "columns": 15,
        "description": "This is a custom dataset uploaded by the user.",
        "created-at": "2024-11-12T10:00:09.611719"
    },
    {
        "id": "compas",
        "name": "ProPublica COMPAS Dataset",
        "size": 2.3,
        "rows": 7214,
        "columns": 12,
        "description": "This dataset contains criminal justice data used to analyze biases in the COMPAS risk assessment algorithm.",
        "created-at": "2024-11-12T10:00:09.611719"
    },
    {
        "id": "credit",
        "name": "German Credit Dataset",
        "size": 1.2,
        "rows": 1000,
        "columns": 20,
        "description": "This dataset provides data on credit risk classification based on personal and financial characteristics.",
        "created-at": "2024-11-12T10:00:09.611719"
    }
  ]'
});

MATCH (pc:PublicContext)
CALL apoc.load.csv("datasets/adult.csv") YIELD map AS row
WITH collect(row) AS adult_data, pc
SET pc.dataset__adult = apoc.convert.toJson(adult_data);

MATCH (pc:PublicContext)
CALL apoc.load.csv("datasets/credit.csv") YIELD map AS row
WITH collect(row) AS credit_data, pc
SET pc.dataset__credit = apoc.convert.toJson(credit_data);

MATCH (pc:PublicContext)
CALL apoc.load.csv("datasets/compas.csv") YIELD map AS row
WITH collect(row) AS compas_data, pc
SET pc.dataset__compas = apoc.convert.toJson(compas_data);
