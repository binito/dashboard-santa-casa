-- ========================================
-- Script de Criação de Utilizador MariaDB
-- Dashboard v8 - Segurança Melhorada
-- ========================================
-- Este script cria um utilizador dedicado 'dashboard_app'
-- com privilégios limitados (princípio do menor privilégio)
-- ========================================

-- 1. CRIAR UTILIZADOR
-- Substitui o uso de 'root' por utilizador dedicado
CREATE USER IF NOT EXISTS 'dashboard_app'@'localhost'
IDENTIFIED BY 'rg0guT1jvTGYImYqmS8CNrtiNHFxY@bP';

-- 2. CONCEDER PRIVILÉGIOS NA BASE DE DADOS 'dashboard'
-- SELECT: Ler dados (consultas)
-- INSERT: Inserir dados (futuros registos)
-- UPDATE: Atualizar dados (futuros registos)
-- DELETE: Apagar dados (manutenção)
GRANT SELECT, INSERT, UPDATE, DELETE ON dashboard.* TO 'dashboard_app'@'localhost';

-- 3. CONCEDER PRIVILÉGIOS NA BASE DE DADOS 'despesify'
-- Apenas SELECT porque o Despesify não deve ser modificado pelo dashboard
GRANT SELECT ON despesify.* TO 'dashboard_app'@'localhost';

-- 4. APLICAR MUDANÇAS
FLUSH PRIVILEGES;

-- 5. VERIFICAR PRIVILÉGIOS (opcional - para debugging)
SHOW GRANTS FOR 'dashboard_app'@'localhost';

-- ========================================
-- NOTAS IMPORTANTES
-- ========================================
-- 1. Este utilizador NÃO tem privilégios administrativos
-- 2. NÃO pode criar/apagar bases de dados (DROP, CREATE DATABASE)
-- 3. NÃO pode criar/apagar tabelas (CREATE TABLE, DROP TABLE)
-- 4. NÃO pode alterar estruturas (ALTER TABLE)
-- 5. NÃO pode gerir outros utilizadores (GRANT, REVOKE)
-- 6. Apenas acesso localhost (não remoto)
-- 7. Despesify: apenas leitura (SELECT)
-- 8. Dashboard: leitura + escrita (SELECT, INSERT, UPDATE, DELETE)
-- ========================================

-- ========================================
-- COMO EXECUTAR ESTE SCRIPT
-- ========================================
-- Opção 1 - Linha de comando:
-- mysql -u root -p < criar_usuario_db.sql
--
-- Opção 2 - Cliente MySQL:
-- mysql -u root -p
-- source /home/jorge/Documentos/Streamlit/criar_usuario_db.sql
--
-- Opção 3 - Direto (copiar e colar no mysql prompt)
-- ========================================

-- ========================================
-- TESTE DE CONEXÃO (após criar utilizador)
-- ========================================
-- mysql -u dashboard_app -p
-- (introduzir senha: rg0guT1jvTGYImYqmS8CNrtiNHFxY@bP)
-- USE dashboard;
-- SHOW TABLES;
-- ========================================
