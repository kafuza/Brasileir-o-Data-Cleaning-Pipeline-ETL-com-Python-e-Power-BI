-- Quantas partidas foram salvas?
SELECT COUNT(*) FROM partidas;

-- Gols por ano
SELECT ano, SUM(total_gols) AS total_gols
FROM partidas
GROUP BY ano
ORDER BY ano;

-- Top 10 times com mais vitórias em casa
SELECT mandante, COUNT(*) AS vitorias
FROM partidas
WHERE resultado = 'Vitória mandante'
GROUP BY mandante
ORDER BY vitorias DESC
LIMIT 10;

-- Distribuição de resultados
SELECT resultado, COUNT(*) AS total,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentual
FROM partidas
GROUP BY resultado;