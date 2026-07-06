"""
Data loader v10.

V10 reutiliza a base robusta do V9 e deixa a camada de dados versionada para
melhorias futuras sem tocar no dashboard atualmente em produção.
"""

from data_loader_v9 import DataLoaderV9


class DataLoaderV10(DataLoaderV9):
    """Carregador V10 baseado no pipeline V9."""

    version = "v10"

    def carregar_tudo_integrado_com_custos(self, data_inicio=None, data_fim=None):
        """
        Carrega todos os dados e adiciona informações de custos.

        Mantém a implementação do V9, mas identifica corretamente a execução nos
        logs da V10.
        """
        print("🚀 Carregando dados do MariaDB (V10 - Cockpit Executivo)...")

        if not self._conectar():
            return super().carregar_tudo_integrado_com_custos(data_inicio, data_fim)

        try:
            df_cafe = self.carregar_dados_dashboard(data_inicio, data_fim)
            df_outros = self.carregar_pos(data_inicio, data_fim)
            df_santa_casa = self.carregar_santa_casa(data_inicio, data_fim)

            dfs = []
            if not df_cafe.empty:
                dfs.append(df_cafe)
            if not df_outros.empty:
                dfs.append(df_outros)
            if not df_santa_casa.empty:
                dfs.append(df_santa_casa)

            if not dfs:
                return super().carregar_tudo_integrado_com_custos(data_inicio, data_fim)

            import pandas as pd

            df_vendas = pd.concat(dfs, ignore_index=True)
            df_vendas = df_vendas.sort_values('Data').reset_index(drop=True)

            df_vendas['Ano'] = df_vendas['Data'].dt.year
            df_vendas['Mes'] = df_vendas['Data'].dt.month
            df_vendas['Semana'] = df_vendas['Data'].dt.isocalendar().week
            df_vendas['Dia_Semana'] = df_vendas['Data'].dt.dayofweek
            df_vendas['Trimestre'] = df_vendas['Data'].dt.quarter

            print(f"📊 Total: {len(df_vendas):,} registos carregados")
            print("💰 Calculando custos e comissões...")

            return self.cost_manager.calcular_custos_vendas(df_vendas)

        finally:
            self._desconectar()
