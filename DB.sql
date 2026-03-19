--Cria o banco de dados do projeto --
CREATE DATABASE brasileirao;

-- Conecta no banco --
\c brasileirao

-- Cria a tabela que vai receber os dados limpos --
CREATE TABLE partidas (
	id 					SERIAL PRIMARY KEY,
	data 				DATE,
	ano					INTEGER,
	mes					INTEGER,
	dia_semana			VARCHAR(20),
	rodada				INTEGER,
	mandante			VARCHAR(60),
	visitante			VARCHAR(60),
	mandante_estado		VARCHAR(30),
	visitante_estado	VARCHAR(30),
	mandante_placar		INTEGER,
	visitante_placar	INTEGER,
	resultado			VARCHAR(30),
	total_gols			INTEGER,
	estadio				VARCHAR(100),
);