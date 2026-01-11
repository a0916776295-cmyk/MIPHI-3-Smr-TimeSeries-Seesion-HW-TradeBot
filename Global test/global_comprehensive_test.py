#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ГЛОБАЛЬНЫЙ КОМПЛЕКСНЫЙ ТЕСТ СИСТЕМЫ ПРОГНОЗИРОВАНИЯ
Полное тестирование всех комбинаций параметров с сохранением результатов
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance import get_finance_data
from Models.model_comparison import compare_all_models
from graph import generate_forecast_graph
from trading_recommendations import calculate_trading_strategy, generate_recommendations_text

class GlobalTestRunner:
    """Класс для проведения глобального тестирования системы"""
    
    def __init__(self):
        self.test_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.results_folder = f"Global test/GlobalTest_{self.test_date}"
        self.comparison_table = []
        self.total_tests = 0
        self.completed_tests = 0
        
        # Создаем папку для результатов
        os.makedirs(self.results_folder, exist_ok=True)
        
    def define_test_parameters(self):
        """Определяем параметры для тестирования"""
        
        # 1. АКТИВЫ для тестирования
        self.test_assets = [
            'NVDA',    # Nvidia - технологии/AI
            'AAPL',    # Apple - технологии
            'MSFT',    # Microsoft - технологии
            'GOOGL',   # Google - технологии
            'AMZN',    # Amazon - e-commerce
            'TSLA',    # Tesla - электромобили
            'META',    # Meta - социальные сети
            'NFLX',    # Netflix - стриминг
            'BRK-B',   # Berkshire - инвестиции
            'JPM'      # JPMorgan - банки
        ]
        
        # 2. СУММЫ ИНВЕСТИЦИЙ (в долларах)
        self.investment_amounts = [
            100,    # Малая сумма
            500,    # Средняя сумма  
            1000,   # Большая сумма
            5000,   # Крупная сумма
            10000   # Максимальная сумма
        ]
        
        # 3. ГОРИЗОНТЫ ПРОГНОЗИРОВАНИЯ (в днях)
        self.forecast_horizons = [
            3,     # Краткосрочный
            5,     # Короткий
            7,     # Недельный
            14,    # Двухнедельный
            21,    # Трехнедельный
            30     # Месячный
        ]
        
        self.total_tests = len(self.test_assets) * len(self.investment_amounts) * len(self.forecast_horizons)
        
        print(f"📊 ПАРАМЕТРЫ ГЛОБАЛЬНОГО ТЕСТА:")
        print(f"   Активы: {len(self.test_assets)} ({', '.join(self.test_assets)})")
        print(f"   Суммы инвестиций: {len(self.investment_amounts)} ({', '.join(map(str, self.investment_amounts))})")
        print(f"   Горизонты прогноза: {len(self.forecast_horizons)} ({', '.join(map(str, self.forecast_horizons))} дней)")
        print(f"   🎯 ОБЩЕЕ КОЛИЧЕСТВО ТЕСТОВ: {self.total_tests}")
        
    def run_single_test(self, asset, amount, forecast_days):
        """Запуск одного теста с заданными параметрами"""
        
        test_name = f"{asset}_{amount}_{forecast_days}days"
        print(f"\n🧪 [{self.completed_tests+1}/{self.total_tests}] Тест: {test_name}")
        
        try:
            # 1. Загружаем данные
            print(f"   📊 Загрузка данных для {asset}...")
            df = get_finance_data(asset)
            if df is None or len(df) < 100:
                print(f"   ❌ Недостаточно данных для {asset}")
                return None
                
            current_price = df['Close'].iloc[-1]
            print(f"   💰 Текущая цена {asset}: ${current_price:.2f}")
            
            # 2. Создаем папку для этого теста
            test_folder = os.path.join(self.results_folder, test_name)
            os.makedirs(test_folder, exist_ok=True)
            
            # 3. Запускаем сравнение моделей (полный режим)
            print(f"   🤖 Запуск сравнения моделей (прогноз на {forecast_days} дней)...")
            start_time = time.time()
            
            best_model, second_best, comparison_data = compare_all_models(
                df, forecast_days, test_folder, fast_mode=False
            )
            
            model_time = time.time() - start_time
            print(f"   ✅ Модели обучены за {model_time:.1f}с")
            
            # 4. Получаем топ-3 модели
            all_models = comparison_data.get('models', [])
            if len(all_models) < 3:
                print(f"   ⚠️ Получено только {len(all_models)} моделей")
                top_3_models = all_models
            else:
                # Сортируем по enhanced_score (чем меньше, тем лучше)
                sorted_models = sorted(all_models, key=lambda x: x.get('enhanced_score', float('inf')))
                top_3_models = sorted_models[:3]
            
            # 5. Генерируем график прогноза
            print(f"   📈 Создание графика прогноза...")
            try:
                graph_path = generate_forecast_graph(
                    df, best_model['predictions'], best_model['model_name'],
                    asset, forecast_days, test_folder
                )
                print(f"   📊 График сохранен: {graph_path}")
            except Exception as graph_error:
                print(f"   ⚠️ Ошибка создания графика: {graph_error}")
                graph_path = None
            
            # 6. Рассчитываем торговую стратегию
            print(f"   💼 Расчет торговой стратегии...")
            try:
                strategy = calculate_trading_strategy(
                    best_model['predictions'], current_price, amount
                )
                recommendations_text = generate_recommendations_text(
                    asset, amount, forecast_days, best_model, strategy
                )
            except Exception as strategy_error:
                print(f"   ⚠️ Ошибка расчета стратегии: {strategy_error}")
                strategy = None
                recommendations_text = "Ошибка расчета"
            
            # 7. Сохраняем результаты теста
            test_result = {
                'test_name': test_name,
                'asset': asset,
                'investment_amount': amount,
                'forecast_days': forecast_days,
                'current_price': float(current_price),
                'test_date': self.test_date,
                'model_training_time': model_time,
                'best_model': {
                    'name': best_model['model_name'],
                    'rmse': float(best_model['rmse']),
                    'mape': float(best_model['mape']),
                    'enhanced_score': float(best_model.get('enhanced_score', 0)),
                    'is_realistic': best_model.get('sanity_check', {}).get('is_valid', False),
                    'predictions': best_model['predictions'].tolist()
                },
                'top_3_models': [],
                'trading_strategy': strategy,
                'recommendations': recommendations_text,
                'graph_path': graph_path
            }
            
            # Добавляем топ-3 модели
            for i, model in enumerate(top_3_models, 1):
                model_info = {
                    'rank': i,
                    'name': model['model_name'],
                    'rmse': float(model['rmse']),
                    'mape': float(model['mape']),
                    'enhanced_score': float(model.get('enhanced_score', 0)),
                    'is_realistic': model.get('is_realistic', False)
                }
                test_result['top_3_models'].append(model_info)
                
                # Добавляем в общую таблицу сравнения
                comparison_row = {
                    'Asset': asset,
                    'Investment': amount,
                    'Forecast_Days': forecast_days,
                    'Model_Rank': i,
                    'Model_Name': model['model_name'],
                    'RMSE': float(model['rmse']),
                    'MAPE': float(model['mape']),
                    'Enhanced_Score': float(model.get('enhanced_score', 0)),
                    'Is_Realistic': model.get('is_realistic', False),
                    'Test_Date': self.test_date,
                    'Training_Time_Sec': model_time
                }
                self.comparison_table.append(comparison_row)
            
            # Сохраняем результат теста в JSON
            result_file = os.path.join(test_folder, f"{test_name}_results.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(test_result, f, ensure_ascii=False, indent=2)
            
            # Сохраняем рекомендации в текстовый файл
            rec_file = os.path.join(test_folder, f"{test_name}_recommendations.txt")
            with open(rec_file, 'w', encoding='utf-8') as f:
                f.write(recommendations_text)
            
            print(f"   ✅ Тест {test_name} завершен успешно")
            return test_result
            
        except Exception as e:
            print(f"   ❌ Ошибка в тесте {test_name}: {str(e)}")
            return None
        finally:
            self.completed_tests += 1
    
    def run_global_test(self):
        """Запуск полного глобального тестирования"""
        
        print(f"🚀 ЗАПУСК ГЛОБАЛЬНОГО КОМПЛЕКСНОГО ТЕСТА")
        print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"📂 Папка результатов: {self.results_folder}")
        print("=" * 70)
        
        start_time = time.time()
        successful_tests = 0
        failed_tests = 0
        
        # Определяем параметры тестирования
        self.define_test_parameters()
        
        # Запускаем тесты
        for asset in self.test_assets:
            print(f"\n📊 АКТИВ: {asset}")
            print("-" * 50)
            
            for amount in self.investment_amounts:
                for forecast_days in self.forecast_horizons:
                    result = self.run_single_test(asset, amount, forecast_days)
                    
                    if result is not None:
                        successful_tests += 1
                        
                        # Показываем прогресс
                        progress = (self.completed_tests / self.total_tests) * 100
                        print(f"   📊 Прогресс: {progress:.1f}% ({self.completed_tests}/{self.total_tests})")
                        
                        # Показываем топ-3 модели для этого теста
                        print("   🏆 Топ-3 модели:")
                        for model in result['top_3_models']:
                            validity = "✅" if model['is_realistic'] else "⚠️"
                            print(f"      {model['rank']}. {model['name']}: RMSE={model['rmse']:.2f}, MAPE={model['mape']:.2f}% {validity}")
                    else:
                        failed_tests += 1
                    
                    # Небольшая пауза между тестами
                    time.sleep(0.5)
        
        # Создаем итоговую таблицу сравнения
        self.create_comparison_table()
        
        # Создаем итоговый отчет
        total_time = time.time() - start_time
        self.create_summary_report(successful_tests, failed_tests, total_time)
        
        print(f"\n🎉 ГЛОБАЛЬНЫЙ ТЕСТ ЗАВЕРШЕН!")
        print(f"✅ Успешно: {successful_tests}")
        print(f"❌ Ошибки: {failed_tests}")
        print(f"⏱️ Общее время: {total_time/60:.1f} минут")
        print(f"📂 Результаты сохранены в: {self.results_folder}")
    
    def create_comparison_table(self):
        """Создание итоговой таблицы сравнения всех результатов"""
        
        if not self.comparison_table:
            print("⚠️ Нет данных для создания таблицы сравнения")
            return
        
        # Создаем DataFrame
        df_comparison = pd.DataFrame(self.comparison_table)
        
        # Сохраняем полную таблицу
        full_table_path = os.path.join(self.results_folder, "Full_Comparison_Table.csv")
        df_comparison.to_csv(full_table_path, index=False, encoding='utf-8')
        
        # Создаем сводные таблицы
        
        # 1. Лучшие модели по активам
        best_by_asset = df_comparison[df_comparison['Model_Rank'] == 1].groupby('Asset').agg({
            'RMSE': 'mean',
            'MAPE': 'mean',
            'Enhanced_Score': 'mean',
            'Is_Realistic': 'mean'
        }).round(2)
        
        asset_summary_path = os.path.join(self.results_folder, "Best_Models_By_Asset.csv")
        best_by_asset.to_csv(asset_summary_path, encoding='utf-8')
        
        # 2. Производительность по горизонтам прогноза
        horizon_summary = df_comparison[df_comparison['Model_Rank'] == 1].groupby('Forecast_Days').agg({
            'RMSE': 'mean',
            'MAPE': 'mean',
            'Enhanced_Score': 'mean',
            'Training_Time_Sec': 'mean'
        }).round(2)
        
        horizon_summary_path = os.path.join(self.results_folder, "Performance_By_Horizon.csv")
        horizon_summary.to_csv(horizon_summary_path, encoding='utf-8')
        
        # 3. Рейтинг моделей
        model_ranking = df_comparison.groupby('Model_Name').agg({
            'RMSE': 'mean',
            'MAPE': 'mean', 
            'Enhanced_Score': 'mean',
            'Is_Realistic': 'mean',
            'Model_Rank': 'mean'
        }).sort_values('Enhanced_Score').round(2)
        
        model_ranking_path = os.path.join(self.results_folder, "Model_Ranking.csv")
        model_ranking.to_csv(model_ranking_path, encoding='utf-8')
        
        print(f"📊 Таблицы сравнения созданы:")
        print(f"   📋 Полная таблица: {full_table_path}")
        print(f"   🏆 По активам: {asset_summary_path}")
        print(f"   ⏰ По горизонтам: {horizon_summary_path}")
        print(f"   🏅 Рейтинг моделей: {model_ranking_path}")
    
    def create_summary_report(self, successful_tests, failed_tests, total_time):
        """Создание итогового отчета"""
        
        report_path = os.path.join(self.results_folder, "GLOBAL_TEST_SUMMARY.md")
        
        report_content = f"""# 📊 ОТЧЕТ ГЛОБАЛЬНОГО ТЕСТИРОВАНИЯ СИСТЕМЫ ПРОГНОЗИРОВАНИЯ

## 📅 Информация о тесте
- **Дата проведения**: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
- **Общее время выполнения**: {total_time/60:.1f} минут
- **Успешных тестов**: {successful_tests}
- **Неудачных тестов**: {failed_tests}
- **Общее количество тестов**: {self.total_tests}

## 🎯 Параметры тестирования
- **Активы**: {', '.join(self.test_assets)} ({len(self.test_assets)} штук)
- **Суммы инвестиций**: {', '.join(map(str, self.investment_amounts))} USD
- **Горизонты прогнозирования**: {', '.join(map(str, self.forecast_horizons))} дней

## 📈 Структура результатов
```
{self.results_folder}/
├── Full_Comparison_Table.csv         # Полная таблица всех результатов
├── Best_Models_By_Asset.csv          # Лучшие модели по активам  
├── Performance_By_Horizon.csv        # Производительность по горизонтам
├── Model_Ranking.csv                 # Общий рейтинг моделей
└── [АКТИВ]_[СУММА]_[ДНЕЙ]days/      # Папки отдельных тестов
    ├── *_results.json                # Детальные результаты
    ├── *_recommendations.txt         # Торговые рекомендации
    └── *_forecast.png               # График прогноза
```

## 🏆 Основные выводы
- Всего протестировано **{len(self.test_assets)} активов** с **{len(self.investment_amounts)} суммами** и **{len(self.forecast_horizons)} горизонтами**
- Получено **{successful_tests}** успешных прогнозов
- Создано **{successful_tests}** графиков прогнозов
- Рассчитано **{successful_tests}** торговых стратегий

## 📊 Файлы анализа
1. **Full_Comparison_Table.csv** - используйте для детального анализа всех результатов
2. **Model_Ranking.csv** - для определения лучших моделей в целом
3. **Best_Models_By_Asset.csv** - для анализа специфики активов
4. **Performance_By_Horizon.csv** - для оценки точности по времени

## 🔧 Следующие шаги
1. Анализ результатов в Excel/Python
2. Выявление закономерностей по активам/горизонтам
3. Оптимизация слабых моделей
4. Настройка параметров для конкретных активов

---
*Сгенерировано системой глобального тестирования {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Итоговый отчет создан: {report_path}")

def main():
    """Главная функция запуска глобального теста"""
    
    print("🌍 ГЛОБАЛЬНОЕ КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("=" * 60)
    
    # Создаем экземпляр тестировщика
    tester = GlobalTestRunner()
    
    # Запрашиваем подтверждение
    print(f"⚠️  ВНИМАНИЕ: Этот тест займет значительное время!")
    print(f"   Планируется {tester.total_tests} тестов")
    print(f"   Примерное время: 2-4 часа")
    
    confirm = input("\n🤔 Продолжить? (да/нет): ").lower().strip()
    
    if confirm in ['да', 'yes', 'y', 'д']:
        print("\n🚀 Запускаем глобальное тестирование...")
        tester.run_global_test()
    else:
        print("\n❌ Тест отменен пользователем")

if __name__ == "__main__":
    main()