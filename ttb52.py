import asyncio
import json
import os
import time
import math
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

# Cấu hình Logging giống tàixỉu-vip.log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("./taixiu-vip.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TaiXiuB52")

app = FastAPI(title="Tai Xiu B52 VIP PRO Advanced")

# ĐĂNG KÝ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

PORT = int(os.environ.get("PORT", 9999))
TARGET_API_URL = "https://serjs-api-b52.onrender.com/api/ditmemayb52"

# Hàm hỗ trợ phân loại mức độ tin cậy
def get_confidence_level(confidence: float) -> str:
    if confidence >= 90: return "SIÊU CAO (99.99%)"
    if confidence >= 80: return "RẤT CAO (90%)"
    if confidence >= 70: return "CAO (80%)"
    if confidence >= 60: return "TRUNG BÌNH (70%)"
    return "THẤP (60%)"

# LỚP THUẬT TOÁN VIP PRO NÂNG CẤP - CÂN BẰNG CẦU VÀ BẺ CẦU THÔNG MINH
class TaiXiuVipProAdvanced:
    def __init__(self):
        self.history: List[int] = []
        self.history_details: List[Dict[str, Any]] = []
        self.max_history_length = 50000
        self.prediction_history: List[Dict[str, Any]] = []
        self.last_processed_phien: Optional[int] = None
        self.consecutive_updates = 0
        self.last_api_fetch_time: Optional[str] = None
        self.api_response_times: List[int] = []
        
        # Cấu hình cầu và bẻ cầu
        self.cau_config = {
            "min_streak_for_cau": 3,
            "max_cau_length": 8,
            "break_cau_threshold": 0.85,
            "min_confidence_for_break": 75,
            "max_recent_caus": 20
        }
        
        # Hiệu suất và thống kê nâng cao
        self.performance_metrics = {
            "overall_accuracy": 0.0,
            "recent_accuracy": 0.0,
            "weekly_accuracy": 0.0,
            "monthly_accuracy": 0.0,
            "streak": {"current": 0, "max": 0},
            "total_predictions": 0,
            "correct_predictions": 0,
            "cau_predictions": {"correct": 0, "total": 0},
            "break_cau_predictions": {"correct": 0, "total": 0},
            "model_performance": {
                "pattern": {"correct": 0, "total": 0, "weight": 0.30},
                "statistical": {"correct": 0, "total": 0, "weight": 0.30},
                "trend": {"correct": 0, "total": 0, "weight": 0.20},
                "neural": {"correct": 0, "total": 0, "weight": 0.10},
                "deep_learning": {"correct": 0, "total": 0, "weight": 0.10} # Gom nhánh deepLearning/timeBased thành DL theo cấu trúc JS gốc
            },
            "time_based_accuracy": {
                "morning": {"correct": 0, "total": 0},
                "afternoon": {"correct": 0, "total": 0},
                "evening": {"correct": 0, "total": 0},
                "night": {"correct": 0, "total": 0}
            }
        }
        
        # Dữ liệu theo thời gian
        self.time_based_patterns = {
            "morning": {"tai": 0, "xiu": 0, "total": 0},
            "afternoon": {"tai": 0, "xiu": 0, "total": 0},
            "evening": {"tai": 0, "xiu": 0, "total": 0},
            "night": {"tai": 0, "xiu": 0, "total": 0}
        }
        
        # Phân tích cầu
        self.cau_analysis = {
            "current_cau": {"type": None, "length": 0, "start_phien": None},
            "recent_caus": [],
            "tai_caus": [],
            "xiu_caus": [],
            "break_efficiency": {"success": 0, "attempts": 0}
        }
        
        self.load_history()
        logger.info("🚀 Thuật Toán VIP Pro Nâng Cấp với Cân Bằng Cầu B52 đã khởi tạo thành công!")

    def save_history(self):
        try:
            data_to_save = {
                "history": self.history,
                "history_details": self.history_details,
                "prediction_history": self.prediction_history,
                "performance_metrics": self.performance_metrics,
                "time_based_patterns": self.time_based_patterns,
                "last_processed_phien": self.last_processed_phien,
                "cau_analysis": self.cau_analysis
            }
            with open('./taixiu_vip_advanced_history.json', 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Lỗi khi lưu lịch sử: {str(e)}")

    def load_history(self):
        try:
            if os.path.exists('./taixiu_vip_advanced_history.json'):
                with open('./taixiu_vip_advanced_history.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.history = data.get("history", [])
                self.history_details = data.get("history_details", [])
                self.prediction_history = data.get("prediction_history", [])
                self.performance_metrics = data.get("performance_metrics", self.performance_metrics)
                self.time_based_patterns = data.get("time_based_patterns", self.time_based_patterns)
                self.last_processed_phien = data.get("last_processed_phien", None)
                self.cau_analysis = data.get("cau_analysis", self.cau_analysis)
                
                logger.info(f"📂 Đã tải lịch sử nâng cao: {len(self.history)} kết quả")
        except Exception as e:
            logger.error(f"❌ Lỗi khi tải lịch sử: {str(e)}")

    def get_time_of_day(self, hour: int) -> str:
        if 5 <= hour < 12: return 'morning'
        if 12 <= hour < 17: return 'afternoon'
        if 17 <= hour < 21: return 'evening'
        return 'night'

    def analyze_current_cau(self) -> Optional[Dict[str, Any]]:
        if len(self.history) < 10: return None
        
        recent_data = self.history[-20:]
        current_type = recent_data[-1]
        current_length = 1
        
        for i in range(len(recent_data) - 2, -1, -1):
            if recent_data[i] == current_type:
                current_length += 1
            else:
                break
                
        return {
            "type": "Tài" if current_type == 1 else "Xỉu",
            "length": current_length,
            "is_cau": current_length >= self.cau_config["min_streak_for_cau"]
        }

    def add_result(self, result: str, phien: int, time_str: Optional[str] = None) -> bool:
        if self.last_processed_phien == phien:
            self.consecutive_updates += 1
            if self.consecutive_updates > 3:
                logger.warning(f"⚠️ Cảnh báo: Phiên {phien} được cập nhật {self.consecutive_updates} lần")
            return False
            
        self.consecutive_updates = 0
        self.last_processed_phien = phien
        
        numeric_result = 1 if result == "Tài" else 0
        self.history.append(numeric_result)
        
        try:
            timestamp = datetime.fromisoformat(time_str.replace("Z", "+00:00")) if time_str else datetime.now()
        except:
            timestamp = datetime.now()
            
        hour = timestamp.hour
        time_of_day = self.get_time_of_day(hour)
        
        if result == "Tài":
            self.time_based_patterns[time_of_day]["tai"] += 1
        else:
            self.time_based_patterns[time_of_day]["xiu"] += 1
        self.time_based_patterns[time_of_day]["total"] += 1
        
        self.history_details.append({
            "Phien": phien,
            "result": result,
            "numericResult": numeric_result,
            "timestamp": timestamp.isoformat(),
            "hour": hour,
            "timeOfDay": time_of_day
        })
        
        self.update_cau_analysis(result, phien)
        
        if len(self.history) > self.max_history_length:
            self.history.pop(0)
            self.history_details.pop(0)
            
        logger.info(f"📊 Added result: {result}, Phien: {phien}, Time: {time_of_day}, Total: {len(self.history)}")
        
        if len(self.history) % 20 == 0:
            self.save_history()
            
        return True

    def update_cau_analysis(self, result: str, phien: int):
        current_cau = self.analyze_current_cau()
        if current_cau and current_cau["is_cau"]:
            if self.cau_analysis["current_cau"]["type"] == current_cau["type"]:
                self.cau_analysis["current_cau"]["length"] = current_cau["length"]
            else:
                if self.cau_analysis["current_cau"]["type"]:
                    old_cau = self.cau_analysis["current_cau"].copy()
                    self.cau_analysis["recent_caus"].append(old_cau)
                    if old_cau["type"] == "Tài":
                        self.cau_analysis["tai_caus"].append(old_cau)
                    else:
                        self.cau_analysis["xiu_caus"].append(old_cau)
                        
                    if len(self.cau_analysis["recent_caus"]) > 50: self.cau_analysis["recent_caus"].pop(0)
                    if len(self.cau_analysis["tai_caus"]) > 100: self.cau_analysis["tai_caus"].pop(0)
                    if len(self.cau_analysis["xiu_caus"]) > 100: self.cau_analysis["xiu_caus"].pop(0)
                    
                self.cau_analysis["current_cau"] = {
                    "type": current_cau["type"],
                    "length": current_cau["length"],
                    "start_phien": int(phien) - current_cau["length"] + 1
                }

    def analyze_break_cau_opportunity(self) -> Dict[str, Any]:
        current_cau = self.cau_analysis["current_cau"]
        if not current_cau or current_cau["length"] < self.cau_config["min_streak_for_cau"]:
            return {"should_break": False, "confidence": 0, "reason": "No current cau"}
            
        same_type_caus = self.cau_analysis["tai_caus"] if current_cau["type"] == "Tài" else self.cau_analysis["xiu_caus"]
        recent_same_type = [c for c in same_type_caus if c["length"] >= self.cau_config["min_streak_for_cau"]]
        
        if not recent_same_type:
            return {"should_break": False, "confidence": 0, "reason": "No historical data"}
            
        ended_at_this_length = len([c for c in recent_same_type if c["length"] == current_cau["length"]])
        continued_at_this_length = len([c for c in recent_same_type if c["length"] > current_cau["length"]])
        total_at_this_length = ended_at_this_length + continued_at_this_length
        
        if total_at_this_length == 0:
            return {"should_break": False, "confidence": 0, "reason": "No data at this length"}
            
        break_probability = ended_at_this_length / total_at_this_length
        break_confidence = min(90.0, break_probability * 100 + (current_cau["length"] - self.cau_config["min_streak_for_cau"]) * 10)
        
        if current_cau["length"] >= self.cau_config["max_cau_length"]:
            return {"should_break": True, "confidence": 95.0, "reason": "Cầu quá dài, xác suất bẻ cao"}
            
        if break_probability >= self.cau_config["break_cau_threshold"] and break_confidence >= self.cau_config["min_confidence_for_break"]:
            return {"should_break": True, "confidence": break_confidence, "reason": f"Tỷ lệ bẻ cầu {(break_probability * 100):.1f}%"}
            
        return {"should_break": False, "confidence": break_confidence, "reason": f"Tỷ lệ bẻ cầu {(break_probability * 100):.1f}% thấp hơn ngưỡng"}

    def advanced_pattern_recognition(self, recent_data: List[int]) -> Dict[str, Any]:
        if len(recent_data) < 20: return {"prediction": "Tài", "confidence": 50.0, "reason": "Không đủ dữ liệu"}
        
        last_twenty = recent_data[-20:]
        tai_count = last_twenty.count(1)
        
        current_streak = 1
        max_streak = 1
        current_type = last_twenty[0]
        streaks = []
        
        for i in range(1, len(last_twenty)):
            if last_twenty[i] == current_type:
                current_streak += 1
            else:
                streaks.append({"type": current_type, "length": current_streak})
                max_streak = max(max_streak, current_streak)
                current_streak = 1
                current_type = last_twenty[i]
        streaks.append({"type": current_type, "length": current_streak})
        max_streak = max(max_streak, current_streak)
        
        if max_streak >= 4:
            long_streak = next((s for s in streaks if s["length"] >= 4), streaks[0])
            confidence = min(85.0, 70.0 + (long_streak["length"] * 5))
            return {
                "prediction": "Xỉu" if long_streak["type"] == 1 else "Tài",
                "confidence": confidence,
                "reason": f"Chuỗi {'Tài' if long_streak['type'] == 1 else 'Xỉu'} dài {long_streak['length']}"
            }
            
        patterns = self.analyze_advanced_patterns(last_twenty)
        if patterns["found"]:
            return patterns
            
        tai_ratio = tai_count / len(last_twenty)
        if abs(tai_ratio - 0.5) > 0.25:
            confidence = min(80.0, 65.0 + abs(tai_ratio - 0.5) * 100)
            return {
                "prediction": "Xỉu" if tai_ratio > 0.5 else "Tài",
                "confidence": confidence,
                "reason": f"Tỷ lệ Tài {(tai_ratio * 100):.1f}%"
            }
            
        last_five = last_twenty[-5:]
        last_five_tai = last_five.count(1)
        last_five_ratio = last_five_tai / 5
        
        if abs(last_five_ratio - 0.5) > 0.4:
            return {
                "prediction": "Tài" if last_five_ratio > 0.5 else "Xỉu",
                "confidence": 70.0,
                "reason": f"Xu hướng gần đây {'Tài' if last_five_ratio > 0.5 else 'Xỉu'} mạnh"
            }
            
        chosen = "Tài" if tai_count >= 10 else "Xỉu"
        return {"prediction": chosen, "confidence": 60.0, "reason": f"Tỷ lệ cân bằng, nghiêng {chosen}"}

    def analyze_advanced_patterns(self, data: List[int]) -> Dict[str, Any]:
        alternating_count = 0
        for i in range(1, len(data)):
            if data[i] != data[i-1]: alternating_count += 1
            
        alternating_ratio = alternating_count / (len(data) - 1)
        if alternating_ratio > 0.8:
            return {
                "found": True,
                "prediction": "Xỉu" if data[-1] == 1 else "Tài",
                "confidence": 75.0,
                "reason": "Mẫu hình xen kẽ mạnh"
            }
            
        cluster_count = 0
        current_cluster = 1
        for i in range(1, len(data)):
            if data[i] == data[i-1]:
                current_cluster += 1
            else:
                if current_cluster >= 2: cluster_count += 1
                current_cluster = 1
        if current_cluster >= 2: cluster_count += 1
        
        if cluster_count >= 3 and len(data) >= 10:
            return {
                "found": True,
                "prediction": "Xỉu" if data[-1] == 1 else "Tài",
                "confidence": 70.0,
                "reason": "Mẫu hình cụm xuất hiện"
            }
            
        return {"found": False, "prediction": "Tài", "confidence": 50.0, "reason": "Không có mẫu hình rõ ràng"}

    def advanced_statistical_analysis(self, recent_data: List[int]) -> Dict[str, Any]:
        full_tai_percentage = recent_data.count(1) / len(recent_data)
        
        short_term = recent_data[-10:]
        medium_term = recent_data[-30:]
        long_term = recent_data[-50:]
        
        short_perc = short_term.count(1) / len(short_term)
        med_perc = medium_term.count(1) / len(medium_term)
        long_perc = long_term.count(1) / len(long_term)
        
        short_dev = abs(short_perc - 0.5)
        med_dev = abs(med_perc - 0.5)
        long_dev = abs(long_perc - 0.5)
        
        if short_dev > 0.3 and short_dev > med_dev and short_dev > long_dev:
            confidence = min(85.0, 65.0 + (short_dev * 50))
            return {
                "prediction": "Xỉu" if short_perc > 0.5 else "Tài",
                "confidence": confidence,
                "reason": f"Điều chỉnh sau độ lệch ngắn hạn {(short_dev * 100):.1f}%"
            }
            
        if long_dev > 0.2 and long_dev > med_dev and long_dev > short_dev:
            confidence = min(80.0, 60.0 + (long_dev * 50))
            return {
                "prediction": "Tài" if long_perc > 0.5 else "Xỉu",
                "confidence": confidence,
                "reason": f"Tiếp tục xu hướng dài hạn {(long_dev * 100):.1f}%"
            }
            
        trend = (short_perc - med_perc) * 100
        if abs(trend) > 15:
            return {
                "prediction": "Tài" if trend > 0 else "Xỉu",
                "confidence": 70.0,
                "reason": f"Xu hướng {'tăng' if trend > 0 else 'giảm'} mạnh"
            }
            
        if abs(full_tai_percentage - 0.5) < 0.1:
            last_ten = recent_data[-10:]
            last_ten_perc = last_ten.count(1) / len(last_ten)
            if abs(last_ten_perc - 0.5) > 0.3:
                return {
                    "prediction": "Xỉu" if last_ten_perc > 0.5 else "Tài",
                    "confidence": 75.0,
                    "reason": "Mean reversion sau biến động mạnh"
                }
                
        return {"prediction": "Tài" if full_tai_percentage >= 0.5 else "Xỉu", "confidence": 55.0, "reason": f"Theo tỷ lệ tổng {(full_tai_percentage * 100):.1f}%"}

    def advanced_trend_analysis(self, recent_data: List[int]) -> Dict[str, Any]:
        if len(recent_data) < 40: return {"prediction": "Tài", "confidence": 50.0, "reason": "Không đủ dữ liệu"}
        
        short_ma = sum(recent_data[-10:]) / 10
        medium_ma = sum(recent_data[-20:]) / 20
        long_ma = sum(recent_data[-40:]) / 40
        
        short_trend = short_ma - medium_ma
        medium_trend = medium_ma - long_ma
        
        if abs(short_trend) > 0.15 and abs(medium_trend) > 0.1:
            if short_trend > 0 and medium_trend > 0:
                return {"prediction": "Tài", "confidence": 78.0, "reason": "Xu hướng Tài mạnh cả ngắn và trung hạn"}
            elif short_trend < 0 and medium_trend < 0:
                return {"prediction": "Xỉu", "confidence": 78.0, "reason": "Xu hướng Xỉu mạnh cả ngắn và trung hạn"}
                
        last_eight = recent_data[-8:]
        eight_trend = self.calculate_slope(last_eight)
        if abs(eight_trend) > 0.25:
            return {"prediction": "Tài" if eight_trend > 0 else "Xỉu", "confidence": 72.0, "reason": f"Đảo chiều {'tăng' if eight_trend > 0 else 'giảm'} mạnh"}
            
        volatility = self.calculate_volatility(recent_data[-15:])
        if volatility > 0.35:
            return {"prediction": "Xỉu" if recent_data[-1] == 1 else "Tài", "confidence": 68.0, "reason": "Biến động cao, dự đoán đảo chiều"}
            
        if short_ma > medium_ma > long_ma:
            return {"prediction": "Tài", "confidence": 75.0, "reason": "Tất cả MA theo xu hướng Tài"}
        elif short_ma < medium_ma < long_ma:
            return {"prediction": "Xỉu", "confidence": 75.0, "reason": "Tất cả MA theo xu hướng Xỉu"}
            
        return {"prediction": "Tài" if short_ma >= 0.5 else "Xỉu", "confidence": 60.0, "reason": f"Theo MA ngắn hạn {short_ma:.2f}"}

    def calculate_slope(self, data: List[int]) -> float:
        n = len(data)
        if n < 2: return 0.0
        x = list(range(n))
        sum_x = sum(x)
        sum_y = sum(data)
        sum_xy = sum(i * data[i] for i in range(n))
        sum_xx = sum(i * i for i in range(n))
        denom = (n * sum_xx - sum_x * sum_x)
        return (n * sum_xy - sum_x * sum_y) / denom if denom != 0 else 0.0

    def calculate_volatility(self, data: List[int]) -> float:
        n = len(data)
        if n < 2: return 0.0
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / n
        return math.sqrt(variance)

    def advanced_neural_network_predict(self, recent_data: List[int]) -> Dict[str, Any]:
        if len(recent_data) < 20: return {"prediction": "Tài", "confidence": 50.0, "reason": "Không đủ dữ liệu"}
        inp = recent_data[-20:]
        
        weights1 = [0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 
                    0.05, 0.04, 0.03, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
        hidden1 = math.tanh(sum(inp[i] * weights1[i] for i in range(20)) * 1.5)
        
        weights2 = [0.18, 0.16, 0.14, 0.12, 0.10, 0.08]
        hidden_inputs = [hidden1] + inp[-5:]
        hidden2 = math.tanh(sum(hidden_inputs[i] * weights2[i] for i in range(6)) * 1.2)
        
        weights3 = [0.25, 0.20, 0.15]
        hidden_inputs2 = [hidden1, hidden2, inp[-1]]
        hidden3 = math.tanh(sum(hidden_inputs2[i] * weights3[i] for i in range(3)))
        
        output_weights = [0.5, 0.3, 0.2]
        output = (hidden1 * output_weights[0] + hidden2 * output_weights[1] + hidden3 * output_weights[2]) * 0.5 + 0.5
        confidence = min(88.0, max(55.0, output * 100))
        
        return {
            "prediction": "Tài" if output > 0.5 else "Xỉu",
            "confidence": round(confidence),
            "reason": f"Neural network output: {output:.3f}"
        }

    def time_based_analysis(self) -> Dict[str, Any]:
        hour = datetime.now().hour
        time_of_day = self.get_time_of_day(hour)
        time_data = self.time_based_patterns[time_of_day]
        
        if time_data["total"] < 20:
            return {"prediction": "Tài", "confidence": 50.0}
            
        tai_percentage = time_data["tai"] / time_data["total"]
        confidence = min(82.0, 55.0 + abs(tai_percentage - 0.5) * 60)
        return {
            "prediction": "Tài" if tai_percentage > 0.5 else "Xỉu",
            "confidence": round(confidence),
            "reason": f"Xu hướng {time_of_day}: Tài {(tai_percentage * 100):.1f}%"
        }

    def advanced_deep_learning_predict(self, input_data: List[int]) -> Dict[str, Any]:
        if len(input_data) < 30: return {"prediction": "Tài", "confidence": 50.0, "reason": "Không đủ dữ liệu"}
        try:
            recent_data = input_data[-30:]
            tai_probability = recent_data.count(1) / len(recent_data)
            sigmoid = lambda x: 1 / (1 + math.exp(-x))
            prediction_value = sigmoid((tai_probability - 0.5) * 6)
            confidence = min(99.9, max(50.1, prediction_value * 100))
            return {
                "prediction": "Tài" if prediction_value > 0.5 else "Xỉu",
                "confidence": round(confidence, 1),
                "reason": f"Deep Learning simulated: {(prediction_value * 100):.1f}%"
            }
        except Exception as e:
            return {"prediction": "Tài", "confidence": 50.0, "reason": f"Lỗi mô hình: {str(e)}"}

    async def predict(self) -> Dict[str, Any]:
        if len(self.history) < 30:
            return {"prediction": "Tài", "confidence": 50.1, "model": "initial", "reason": "Chưa đủ dữ liệu lịch sử"}
            
        recent = self.history[-100:]
        current_cau = self.analyze_current_cau()
        break_opportunity = self.analyze_break_cau_opportunity()
        
        predictions = {
            "pattern": self.advanced_pattern_recognition(recent),
            "statistical": self.advanced_statistical_analysis(recent),
            "trend": self.advanced_trend_analysis(recent),
            "neural": self.advanced_neural_network_predict(recent),
            "deep_learning": self.advanced_deep_learning_predict(recent),
            "time_based": self.time_based_analysis()
        }
        
        if break_opportunity["should_break"] and break_opportunity["confidence"] >= 75:
            break_prediction = "Xỉu" if current_cau["type"] == "Tài" else "Tài"
            return {
                "prediction": break_prediction,
                "confidence": break_opportunity["confidence"],
                "model": "break_cau",
                "reason": f"Bẻ cầu {current_cau['type']} dài {current_cau['length']} - {break_opportunity['reason']}",
                "details": {"breakAnalysis": break_opportunity, "currentCau": current_cau, "modelPredictions": predictions}
            }
            
        tai_score = 0.0
        total_weight = 0.0
        reasons = []
        
        for model, pred in predictions.items():
            weight = self.performance_metrics["model_performance"].get(model, {"weight": 0.1})["weight"]
            if pred["prediction"] == "Tài":
                tai_score += pred["confidence"] * weight
            else:
                tai_score -= pred["confidence"] * weight
            total_weight += weight
            reasons.append(f"{model}: {pred['prediction']} ({pred['confidence']}%)")
            
        confidence = 50.0 + (tai_score / total_weight)
        confidence = max(61.0, min(97.0, confidence))
        confidence = math.floor(confidence * 10) / 10
        if confidence % 1 == 0: confidence += 0.1
        
        final_prediction = "Tài" if confidence >= 50 else "Xỉu"
        
        if self.performance_metrics["recent_accuracy"] < 0.45:
            return {
                "prediction": "Xỉu" if final_prediction == "Tài" else "Tài",
                "confidence": 100.0 - confidence,
                "model": "ensemble_adjusted",
                "reason": f"Điều chỉnh ngược do hiệu suất gần đây thấp ({(self.performance_metrics['recent_accuracy'] * 100):.1f}%)",
                "details": predictions
            }
            
        if current_cau and current_cau["is_cau"] and current_cau["length"] >= 5:
            if final_prediction == current_cau["type"]:
                adjusted_prediction = "Xỉu" if final_prediction == "Tài" else "Tài"
                return {
                    "prediction": adjusted_prediction,
                    "confidence": min(85.0, confidence + 5),
                    "model": "cau_adjusted",
                    "reason": f"Điều chỉnh do cầu {current_cau['type']} dài {current_cau['length']}",
                    "details": {"originalPrediction": final_prediction, "originalConfidence": confidence, "currentCau": current_cau, "modelPredictions": predictions}
                }
                
        return {
            "prediction": final_prediction,
            "confidence": confidence,
            "model": "ensemble",
            "reason": f"Kết hợp {', '.join(reasons)}",
            "details": predictions
        }

    def update_performance(self, actual_result: str):
        if not self.prediction_history: return
        
        last_prediction = self.prediction_history[-1]
        was_correct = last_prediction["prediction"] == actual_result
        
        self.performance_metrics["total_predictions"] += 1
        if was_correct:
            self.performance_metrics["correct_predictions"] += 1
            self.performance_metrics["streak"]["current"] += 1
            if self.performance_metrics["streak"]["current"] > self.performance_metrics["streak"]["max"]:
                self.performance_metrics["streak"]["max"] = self.performance_metrics["streak"]["current"]
        else:
            self.performance_metrics["streak"]["current"] = 0
            
        current_cau = self.analyze_current_cau()
        if current_cau and current_cau["is_cau"]:
            self.performance_metrics["cau_predictions"]["total"] += 1
            if was_correct: self.performance_metrics["cau_predictions"]["correct"] += 1
            
        if last_prediction["model"] == "break_cau":
            self.performance_metrics["break_cau_predictions"]["total"] += 1
            if was_correct:
                self.performance_metrics["break_cau_predictions"]["correct"] += 1
                self.cau_analysis["break_efficiency"]["success"] += 1
            self.cau_analysis["break_efficiency"]["attempts"] += 1
            
        time_of_day = self.get_time_of_day(datetime.now().hour)
        self.performance_metrics["time_based_accuracy"][time_of_day]["total"] += 1
        if was_correct: self.performance_metrics["time_based_accuracy"][time_of_day]["correct"] += 1
        
        self.performance_metrics["overall_accuracy"] = self.performance_metrics["correct_predictions"] / self.performance_metrics["total_predictions"]
        
        recent_preds = self.prediction_history[-50:]
        if len(recent_preds) > 10:
            recent_results = self.history_details[-50:]
            correct_recent = 0
            match_len = min(len(recent_preds), len(recent_results))
            for i in range(match_len):
                if recent_preds[i]["prediction"] == recent_results[i]["result"]: correct_recent += 1
            self.performance_metrics["recent_accuracy"] = correct_recent / match_len
            
        if "details" in last_prediction:
            self.adjust_model_weights(was_correct, last_prediction["details"])
            
        if self.performance_metrics["total_predictions"] % 10 == 0:
            self.save_history()

    def adjust_model_weights(self, was_correct: bool, model_predictions: Dict[str, Any]):
        if self.performance_metrics["total_predictions"] < 30: return
        
        for model, pred in model_predictions.items():
            if model in self.performance_metrics["model_performance"]:
                self.performance_metrics["model_performance"][model]["total"] += 1
                expected = pred["prediction"] if was_correct else ("Xỉu" if pred["prediction"] == "Tài" else "Tài")
                if pred["prediction"] == expected:
                    self.performance_metrics["model_performance"][model]["correct"] += 1
                    
        total_accuracy = 0.0
        accuracies = {}
        for model, data in self.performance_metrics["model_performance"].items():
            acc = data["correct"] / data["total"] if data["total"] > 0 else 0.5
            accuracies[model] = acc
            total_accuracy += acc
            
        if total_accuracy > 0:
            for model in accuracies:
                self.performance_metrics["model_performance"][model]["weight"] = accuracies[model] / total_accuracy
                
        min_weight = 0.08
        for model in self.performance_metrics["model_performance"]:
            self.performance_metrics["model_performance"][model]["weight"] = max(min_weight, self.performance_metrics["model_performance"][model]["weight"])
            
        total_weight = sum(m["weight"] for m in self.performance_metrics["model_performance"].values())
        for model in self.performance_metrics["model_performance"]:
            self.performance_metrics["model_performance"][model]["weight"] /= total_weight

    def get_advanced_analysis(self) -> Dict[str, Any]:
        if len(self.history) < 30: return {"message": "Cần thêm dữ liệu để phân tích"}
        recent = self.history[-100:]
        tai_count = recent.count(1)
        tai_percentage = (tai_count / len(recent)) * 100
        
        changes = sum(1 for i in range(1, len(recent)) if recent[i] != recent[i-1])
        volatility = (changes / (len(recent) - 1)) * 100
        
        max_tai_streak, max_xiu_streak, current_streak = 0, 0, 1
        current_type = recent[0]
        
        for i in range(1, len(recent)):
            if recent[i] == current_type: current_streak += 1
            else:
                if current_type == 1: max_tai_streak = max(max_tai_streak, current_streak)
                else: max_xiu_streak = max(max_xiu_streak, current_streak)
                current_streak = 1
                current_type = recent[i]
        if current_type == 1: max_tai_streak = max(max_tai_streak, current_streak)
        else: max_xiu_streak = max(max_xiu_streak, current_streak)
        
        model_accuracies = {m: (f"{(d['correct']/d['total']*100):.1f}" if d['total'] > 0 else "0.0") for m, d in self.performance_metrics["model_performance"].items()}
        time_analysis = {t: {"tai_percentage": f"{(d['tai']/d['total']*100):.1f}%", "total": d['total']} for t, d in self.time_based_patterns.items() if d['total'] > 0}
        
        current_cau = self.analyze_current_cau()
        break_opportunity = self.analyze_break_cau_opportunity()
        
        cau_eff = (self.performance_metrics["cau_predictions"]["correct"] / self.performance_metrics["cau_predictions"]["total"] * 100) if self.performance_metrics["cau_predictions"]["total"] > 0 else 0.0
        break_eff = (self.performance_metrics["break_cau_predictions"]["correct"] / self.performance_metrics["break_cau_predictions"]["total"] * 100) if self.performance_metrics["break_cau_predictions"]["total"] > 0 else 0.0
        
        return {
            "recent_tai_percentage": f"{tai_percentage:.1f}%",
            "volatility": f"{volatility:.1f}%",
            "max_tai_streak": max_tai_streak,
            "max_xiu_streak": max_xiu_streak,
            "current_cau": current_cau,
            "break_opportunity": break_opportunity,
            "cau_efficiency": f"{cau_eff:.1f}%",
            "break_efficiency": f"{break_eff:.1f}%",
            "model_weights": {k: round(v["weight"] * 100) for k, v in self.performance_metrics["model_performance"].items()},
            "model_accuracy": model_accuracies,
            "time_analysis": time_analysis,
            "suggestion": "Xu hướng Tài mạnh" if tai_percentage > 70 else ("Xu hướng Xỉu mạnh" if tai_percentage < 30 else "Xu hướng không rõ ràng"),
            "recommended_action": "Theo dõi thêm, thị trường biến động mạnh" if volatility > 60 else "Có thể đặt cược theo xu hướng"
        }

# Khởi tạo instance thuật toán
taiXiuPredictor = TaiXiuVipProAdvanced()

# VÒNG LẶP ĐỒNG BỘ DỮ LIỆU TỰ ĐỘNG TỪ API B52 GỐC
async def fetch_taixiu_data_with_retry(retries=5, delay=1.0) -> Optional[Dict[str, Any]]:
    import httpx
    async with httpx.AsyncClient() as client:
        for i in range(retries):
            try:
                start_time = time.time()
                response = await client.get(TARGET_API_URL, timeout=10.0, headers={
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                end_time = time.time()
                taiXiuPredictor.api_response_times.append(int((end_time - start_time) * 1000))
                if len(taiXiuPredictor.api_response_times) > 100: taiXiuPredictor.api_response_times.pop(0)
                
                taiXiuPredictor.last_api_fetch_time = datetime.now().isoformat()
                
                # Khớp trường dữ liệu theo JSON B52 của bạn
                data = response.json()
                if isinstance(data, list) and len(data) > 0: data = data[0] # Khử mảng nếu API trả về list
                return data
            except Exception as e:
                logger.error(f"❌ Lỗi khi lấy dữ liệu B52 (lần {i+1}): {str(e)}")
                if i < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    return None

async def update_taixiu_data_loop():
    await asyncio.sleep(2.0) # Khởi động trễ lần đầu
    while True:
        try:
            data = await fetch_taixiu_data_with_retry()
            if data and "Phien" in data and "Ket_qua" in data:
                # Ép kiểu dữ liệu an toàn
                phien = int(data["Phien"])
                ket_qua = str(data["Ket_qua"])
                
                added = taiXiuPredictor.add_result(ket_qua, phien, datetime.now().isoformat())
                if added:
                    logger.info(f"📥 Đã cập nhật phiên B52 {phien} → {ket_qua}")
                    if taiXiuPredictor.prediction_history:
                        taiXiuPredictor.update_performance(ket_qua)
                        
                    prediction = await taiXiuPredictor.predict()
                    taiXiuPredictor.prediction_history.append({
                        **prediction,
                        "timestamp": datetime.now().isoformat(),
                        "phien": phien + 1
                    })
                    if len(taiXiuPredictor.prediction_history) > 200: taiXiuPredictor.prediction_history.pop(0)
        except Exception as e:
            logger.error(f"❌ Lỗi vòng lặp cập nhật dữ liệu: {str(e)}")
        await asyncio.sleep(5) # Mỗi 5 giây chạy lại như cấu hình Nodejs

async def periodic_save_loop():
    while True:
        await asyncio.sleep(300) # Mỗi 5 phút sao lưu file
        taiXiuPredictor.save_history()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_taixiu_data_loop())
    asyncio.create_task(periodic_save_loop())

# --- CÁC ROUTE API PHƠI RA NGOÀI ---

@app.get("/api/taixiu/du-doan")
async def get_simple_predict():
    data = await fetch_taixiu_data_with_retry()
    if not data or "Phien" not in data:
        return {"success": False, "message": "Không thể lấy dữ liệu từ API", "du_doan": "Chưa đủ dữ liệu", "do_tin_cay": 0}
        
    prediction = await taiXiuPredictor.predict()
    next_phien = int(data["Phien"]) + 1
    
    return {
        "success": True,
        "Phien": data["Phien"],
        "phien_hien_tai": next_phien,
        "du_doan": prediction["prediction"],
        "do_tin_cay": prediction["confidence"],
        "muc_do_tin_cay": get_confidence_level(prediction["confidence"]),
        "do_chinh_xac": round(taiXiuPredictor.performance_metrics["overall_accuracy"] * 100),
        "so_lan_du_doan": taiXiuPredictor.performance_metrics["total_predictions"],
        "chuoi_chinh_xac": taiXiuPredictor.performance_metrics["streak"]["current"],
        "ly_do": prediction["reason"]
    }

@app.get("/api/taixiu/b52/predict")
async def get_advanced_predict():
    data = await fetch_taixiu_data_with_retry()
    if not data or "Phien" not in data:
        return {"success": False, "message": "Không thể lấy dữ liệu từ API B52", "du_doan": "Chưa đủ dữ liệu", "do_tin_cay": 0}
        
    prediction = await taiXiuPredictor.predict()
    next_phien = int(data["Phien"]) + 1
    
    return {
        "success": True,
        "Phien": data.get("Phien"),
        "Xuc_xac_1": data.get("Xuc_xac_1"),
        "Xuc_xac_2": data.get("Xuc_xac_2"),
        "Xuc_xac_3": data.get("Xuc_xac_3"),
        "Tong": data.get("Tong"),
        "Ket_qua": data.get("Ket_qua"),
        "phien_hien_tai": next_phien,
        "du_doan": prediction["prediction"],
        "do_tin_cay": prediction["confidence"],
        "muc_do_tin_cay": get_confidence_level(prediction["confidence"]),
        "mo_hinh": prediction["model"],
        "ly_do": prediction["reason"],
        "lich_su": len(taiXiuPredictor.history)
    }

@app.get("/api/taixiu/b52")
async def get_raw_data():
    data = await fetch_taixiu_data_with_retry()
    if not data: return {"success": False, "message": "Không thể lấy dữ liệu từ API B52"}
    return {"success": True, **data}

@app.get("/api/taixiu/phan-tich")
async def get_analysis():
    avg_res = round(sum(taiXiuPredictor.api_response_times) / len(taiXiuPredictor.api_response_times)) if taiXiuPredictor.api_response_times else 0
    return {
        "success": True,
        "algorithm_status": "VIP PRO ADVANCED ALGORITHM - CÂN BẰNG CẦU VÀ BẺ CẦU THÔNG MINH B52",
        "model_status": {
            "data_points": len(taiXiuPredictor.history),
            "overall_accuracy": round(taiXiuPredictor.performance_metrics["overall_accuracy"] * 100, 2),
            "recent_accuracy": round(taiXiuPredictor.performance_metrics["recent_accuracy"] * 100, 2),
            "current_streak": taiXiuPredictor.performance_metrics["streak"]["current"],
            "max_streak": taiXiuPredictor.performance_metrics["streak"]["max"],
            "total_predictions": taiXiuPredictor.performance_metrics["total_predictions"],
            "correct_predictions": taiXiuPredictor.performance_metrics["correct_predictions"],
            "cau_accuracy": round(taiXiuPredictor.performance_metrics["cau_predictions"]["correct"] / taiXiuPredictor.performance_metrics["cau_predictions"]["total"] * 100, 2) if taiXiuPredictor.performance_metrics["cau_predictions"]["total"] > 0 else 0,
            "break_accuracy": round(taiXiuPredictor.performance_metrics["break_cau_predictions"]["correct"] / taiXiuPredictor.performance_metrics["break_cau_predictions"]["total"] * 100, 2) if taiXiuPredictor.performance_metrics["break_cau_predictions"]["total"] > 0 else 0
        },
        "analysis": taiXiuPredictor.get_advanced_analysis(),
        "last_update": taiXiuPredictor.last_api_fetch_time,
        "avg_response_time": avg_res
    }

@app.get("/api/taixiu/lich-su")
async def get_history(limit: int = Query(20, le=100)):
    predictions = []
    sliced_preds = taiXiuPredictor.prediction_history[-limit:]
    for index, pred in enumerate(sliced_preds):
        actual_index = len(taiXiuPredictor.prediction_history) - len(sliced_preds) + index
        actual_result = taiXiuPredictor.history_details[actual_index]["result"] if actual_index >= 0 and actual_index < len(taiXiuPredictor.history_details) else 'N/A'
        predictions.append({
            "stt": actual_index + 1,
            "phien": pred.get("phien", taiXiuPredictor.history_details[actual_index]["Phien"] if actual_index >= 0 else 'N/A'),
            "du_doan": pred["prediction"],
            "thuc_te": actual_result,
            "trang_thai": "Đúng" if pred["prediction"] == actual_result else "Sai",
            "do_tin_cay": pred["confidence"],
            "mo_hinh": pred["model"],
            "ly_do": pred["reason"]
        })
    predictions.reverse()
    return {"success": True, "predictions": predictions, "total": len(taiXiuPredictor.prediction_history)}

@app.get("/api/taixiu/ket-qua")
async def get_results(limit: int = Query(50, le=200)):
    sliced_details = taiXiuPredictor.history_details[-limit:]
    sliced_details.reverse()
    results = [{
        "Phien": item["Phien"],
        "Ket_qua": item["result"],
        "thoi_gian": item["timestamp"],
        "gio": item["hour"],
        "khoang_thoi_gian": item["timeOfDay"]
    } for item in sliced_details]
    return {"success": True, "results": results, "total": len(taiXiuPredictor.history_details)}

@app.get("/health")
async def health_check():
    import sys
    uptime = time.monotonic() # Thời gian server chạy nhại bén
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "history_size": len(taiXiuPredictor.history),
        "predictions_count": len(taiXiuPredictor.prediction_history),
        "accuracy": round(taiXiuPredictor.performance_metrics["overall_accuracy"] * 100, 2),
        "api_response_times": taiXiuPredictor.api_response_times[-10:]
    }

@app.delete("/api/taixiu/lich-su")
async def clear_history(password: str = Query(...), response: Response = None):
    if password != 'admin123':
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"success": False, "message": "Không có quyền thực hiện hành động này"}
        
    global taiXiuPredictor
    taiXiuPredictor = TaiXiuVipProAdvanced()
    if os.path.exists('./taixiu_vip_advanced_history.json'):
        os.remove('./taixiu_vip_advanced_history.json')
    return {"success": True, "message": "Đã xóa toàn bộ lịch sử và thiết lập lại thuật toán B52"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"📈 API B52 Khởi chạy tại Port: {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)