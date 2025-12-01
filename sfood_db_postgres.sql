-- ======================================================
-- SCHEMA sfood (você pode usar o padrão "public" também)
-- ======================================================

-- No Supabase normalmente já está usando "public".
-- Se quiser separar, pode criar schema:
-- CREATE SCHEMA IF NOT EXISTS sfood;
-- SET search_path TO sfood,public;

-- Para simplificar, vou usar o schema padrão "public".

-- ======================================================
-- TABELA: usuarios
-- ======================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id              BIGSERIAL PRIMARY KEY,
    nome            VARCHAR(150) NOT NULL,
    email           VARCHAR(180) UNIQUE NOT NULL,
    senha_hash      VARCHAR(255) NOT NULL,
    tipo            TEXT NOT NULL DEFAULT 'operador'
                    CHECK (tipo IN ('cliente', 'operador', 'ceo', 'admin')),
    ultimo_login    TIMESTAMP NULL,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ======================================================
-- TABELA: clientes
-- ======================================================

CREATE TABLE IF NOT EXISTS clientes (
    id                  BIGSERIAL PRIMARY KEY,
    usuario_id          BIGINT NULL REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE,
    nome                VARCHAR(150) NOT NULL,
    email               VARCHAR(180) NOT NULL,
    telefone            VARCHAR(30),
    cep                 VARCHAR(12),
    cidade              VARCHAR(100),
    uf                  CHAR(2),
    tipo_familia        TEXT DEFAULT 'outro'
                        CHECK (tipo_familia IN ('solteiro','casal','familia_pequena','familia_grande','outro')),
    preferencia_dieta   TEXT DEFAULT 'nenhuma'
                        CHECK (preferencia_dieta IN ('nenhuma','saudavel','fit','vegetariana','vegana','low_carb')),
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW(),
    atualizado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);

-- ======================================================
-- TABELA: categorias_produto
-- ======================================================

CREATE TABLE IF NOT EXISTS categorias_produto (
    id          BIGSERIAL PRIMARY KEY,
    nome        VARCHAR(120) NOT NULL,
    slug        VARCHAR(120) UNIQUE NOT NULL
);

-- ======================================================
-- TABELA: produtos
-- ======================================================

CREATE TABLE IF NOT EXISTS produtos (
    id                  BIGSERIAL PRIMARY KEY,
    nome                VARCHAR(150) NOT NULL,
    descricao           TEXT,
    categoria_id        BIGINT REFERENCES categorias_produto(id) ON DELETE SET NULL ON UPDATE CASCADE,
    preco               NUMERIC(10,2) NOT NULL,
    unidade             VARCHAR(20) DEFAULT 'un',
    eh_saudavel         BOOLEAN NOT NULL DEFAULT FALSE,
    tags_texto          VARCHAR(255),
    ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW(),
    atualizado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_produtos_ativo ON produtos(ativo);

-- ======================================================
-- TABELA: pedidos
-- ======================================================

CREATE TABLE IF NOT EXISTS pedidos (
    id                  BIGSERIAL PRIMARY KEY,
    cliente_id          BIGINT NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    data_criado         TIMESTAMP NOT NULL DEFAULT NOW(),
    status              TEXT NOT NULL DEFAULT 'novo'
                        CHECK (status IN ('novo','em_preparo','enviado','entregue','cancelado')),
    tipo_pedido         TEXT NOT NULL DEFAULT 'avulso'
                        CHECK (tipo_pedido IN ('avulso','assinatura','teste')),
    origem              TEXT NOT NULL DEFAULT 'app'
                        CHECK (origem IN ('app','intranet','teste_demo')),
    valor_subtotal      NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    valor_descontos     NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    valor_frete         NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    valor_total         NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    assinatura_id       BIGINT NULL,
    observacoes         VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos(status);
CREATE INDEX IF NOT EXISTS idx_pedidos_tipo ON pedidos(tipo_pedido);

-- ======================================================
-- TABELA: itens_pedido
-- ======================================================

CREATE TABLE IF NOT EXISTS itens_pedido (
    id              BIGSERIAL PRIMARY KEY,
    pedido_id       BIGINT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE ON UPDATE CASCADE,
    produto_id      BIGINT NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    quantidade      INTEGER NOT NULL DEFAULT 1,
    preco_unitario  NUMERIC(10,2) NOT NULL,
    subtotal        NUMERIC(10,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido ON itens_pedido(pedido_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_produto ON itens_pedido(produto_id);

-- ======================================================
-- TABELA: assinaturas
-- ======================================================

CREATE TABLE IF NOT EXISTS assinaturas (
    id                  BIGSERIAL PRIMARY KEY,
    cliente_id          BIGINT NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    nome_plano          VARCHAR(150) NOT NULL,
    descricao_curta     VARCHAR(255),
    frequencia          TEXT NOT NULL DEFAULT 'semanal'
                        CHECK (frequencia IN ('semanal','quinzenal','mensal')),
    ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    data_inicio         DATE NOT NULL,
    data_fim            DATE,
    proxima_entrega     DATE,
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW(),
    atualizado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assinaturas_cliente ON assinaturas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_assinaturas_ativo ON assinaturas(ativo);

-- ======================================================
-- TABELA: planos_refeicoes
-- ======================================================

CREATE TABLE IF NOT EXISTS planos_refeicoes (
    id                      BIGSERIAL PRIMARY KEY,
    cliente_id              BIGINT NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    assinatura_id           BIGINT REFERENCES assinaturas(id) ON DELETE SET NULL ON UPDATE CASCADE,
    data_inicio_semana      DATE NOT NULL,
    objetivo                TEXT NOT NULL DEFAULT 'saudavel'
                            CHECK (objetivo IN ('saudavel','praticidade','economia','familia_criancas','outro')),
    restricoes_texto        VARCHAR(255),
    criado_em               TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_planos_refeicoes_cliente ON planos_refeicoes(cliente_id);

-- ======================================================
-- TABELA: planos_refeicoes_dias
-- ======================================================

CREATE TABLE IF NOT EXISTS planos_refeicoes_dias (
    id                      BIGSERIAL PRIMARY KEY,
    plano_id                BIGINT NOT NULL REFERENCES planos_refeicoes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    dia_semana              TEXT NOT NULL
                            CHECK (dia_semana IN ('segunda','terca','quarta','quinta','sexta','sabado','domingo')),
    refeicao_tipo           TEXT NOT NULL
                            CHECK (refeicao_tipo IN ('cafe','almoco','jantar','snack')),
    descricao_refeicao      VARCHAR(255) NOT NULL,
    produto_id_sugerido     BIGINT REFERENCES produtos(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_planos_dias_plano ON planos_refeicoes_dias(plano_id);
CREATE INDEX IF NOT EXISTS idx_planos_dias_dia ON planos_refeicoes_dias(dia_semana);

-- ======================================================
-- TABELA: faq (base chatbot)
-- ======================================================

CREATE TABLE IF NOT EXISTS faq (
    id              BIGSERIAL PRIMARY KEY,
    pergunta        TEXT NOT NULL,
    resposta        TEXT NOT NULL,
    tags            VARCHAR(255),
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    atualizado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ======================================================
-- TABELA: chatbot_logs
-- ======================================================

CREATE TABLE IF NOT EXISTS chatbot_logs (
    id              BIGSERIAL PRIMARY KEY,
    cliente_id      BIGINT REFERENCES clientes(id) ON DELETE SET NULL ON UPDATE CASCADE,
    origem          TEXT NOT NULL DEFAULT 'cliente'
                    CHECK (origem IN ('cliente','intranet','ceo')),
    pergunta        TEXT NOT NULL,
    resposta        TEXT,
    confianca       DOUBLE PRECISION,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chatbot_logs_cliente ON chatbot_logs(cliente_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_logs_origem ON chatbot_logs(origem);

-- ======================================================
-- TABELA: promocoes_ia
-- ======================================================

CREATE TABLE IF NOT EXISTS promocoes_ia (
    id                  BIGSERIAL PRIMARY KEY,
    titulo              VARCHAR(150) NOT NULL,
    descricao           TEXT,
    publico_alvo        VARCHAR(255),
    desconto_sugerido   NUMERIC(5,2),
    status              TEXT NOT NULL DEFAULT 'sugerida'
                        CHECK (status IN ('sugerida','aplicada','descartada')),
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW(),
    aplicada_em         TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_promocoes_status ON promocoes_ia(status);

-- ======================================================
-- SEEDS BÁSICOS
-- ======================================================

INSERT INTO categorias_produto (nome, slug) VALUES
    ('Café da manhã', 'cafe_da_manha'),
    ('Refeições prontas', 'refeicoes_prontas'),
    ('Hortifruti', 'hortifruti')
ON CONFLICT (slug) DO UPDATE SET nome = EXCLUDED.nome;

INSERT INTO produtos (nome, descricao, categoria_id, preco, unidade, eh_saudavel, tags_texto)
VALUES
    ('Kit Café da Manhã Família', 'Itens para 7 dias de café da manhã em família.', 1, 89.90, 'kit', TRUE,
     'cafe_da_manha;familia;praticidade;saudavel'),
    ('Box Refeições Fit Semanal', '10 refeições fit prontas para a semana.', 2, 149.90, 'box', TRUE,
     'refeicoes_prontas;fit;semana;saudavel'),
    ('Cesta de Frutas Premium', 'Seleção de frutas frescas e premium.', 3, 59.90, 'cesta', TRUE,
     'hortifruti;frutas;saudavel');
