from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class MoodEntry:
    """Represents a single mood entry"""
    
    def __init__(self, mood_score: int, notes: str = "", stress_level: int = 5, 
                 energy_level: int = 5, sleep_hours: float = 8.0, tags: List[str] = None):
        self.timestamp = datetime.now()
        self.mood_score = mood_score  # 1-10 scale
        self.notes = notes
        self.stress_level = stress_level  # 1-10 scale
        self.energy_level = energy_level  # 1-10 scale
        self.sleep_hours = sleep_hours
        self.tags = tags or []
        
    def to_dict(self) -> Dict:
        """Convert mood entry to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'mood_score': self.mood_score,
            'notes': self.notes,
            'stress_level': self.stress_level,
            'energy_level': self.energy_level,
            'sleep_hours': self.sleep_hours,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MoodEntry':
        """Create MoodEntry from dictionary"""
        entry = cls(
            mood_score=data['mood_score'],
            notes=data.get('notes', ''),
            stress_level=data.get('stress_level', 5),
            energy_level=data.get('energy_level', 5),
            sleep_hours=data.get('sleep_hours', 8.0),
            tags=data.get('tags', [])
        )
        if 'timestamp' in data:
            entry.timestamp = datetime.fromisoformat(data['timestamp'])
        return entry

class MoodTracker:
    """Main mood tracking functionality"""
    
    def __init__(self, sheets_api=None):
        self.entries = []
        self.sheets_api = sheets_api
        
    def add_entry(self, mood_entry: MoodEntry) -> bool:
        """Add a new mood entry"""
        try:
            self.entries.append(mood_entry)
            
            # Save to Google Sheets if available
            if self.sheets_api:
                self.sheets_api.add_mood_entry(mood_entry)
                
            return True
        except Exception as e:
            print(f"Error adding mood entry: {e}")
            return False
    
    def get_recent_entries(self, days: int = 7) -> List[MoodEntry]:
        """Get mood entries from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [entry for entry in self.entries if entry.timestamp >= cutoff_date]
    
    def get_mood_trends(self, days: int = 30) -> Dict:
        """Calculate mood trends and statistics"""
        recent_entries = self.get_recent_entries(days)
        
        if not recent_entries:
            return {'error': 'No entries found'}
        
        mood_scores = [entry.mood_score for entry in recent_entries]
        stress_levels = [entry.stress_level for entry in recent_entries]
        energy_levels = [entry.energy_level for entry in recent_entries]
        sleep_hours = [entry.sleep_hours for entry in recent_entries]
        
        return {
            'total_entries': len(recent_entries),
            'avg_mood': sum(mood_scores) / len(mood_scores),
            'avg_stress': sum(stress_levels) / len(stress_levels),
            'avg_energy': sum(energy_levels) / len(energy_levels),
            'avg_sleep': sum(sleep_hours) / len(sleep_hours),
            'mood_trend': self._calculate_trend(mood_scores),
            'date_range': {
                'start': recent_entries[-1].timestamp.date().isoformat(),
                'end': recent_entries[0].timestamp.date().isoformat()
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate if trend is improving, declining, or stable"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Simple trend calculation - compare first and second half averages
        mid_point = len(values) // 2
        first_half_avg = sum(values[:mid_point]) / mid_point
        second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 0.5:
            return 'improving'
        elif diff < -0.5:
            return 'declining'
        else:
            return 'stable'
    
    def search_entries_by_tag(self, tag: str) -> List[MoodEntry]:
        """Search entries by tag"""
        return [entry for entry in self.entries if tag.lower() in [t.lower() for t in entry.tags]]
    
    def get_mood_patterns(self) -> Dict:
        """Analyze patterns in mood data"""
        if not self.entries:
            return {'error': 'No entries found'}
        
        # Group by day of week
        weekday_moods = {i: [] for i in range(7)}
        for entry in self.entries:
            weekday_moods[entry.timestamp.weekday()].append(entry.mood_score)
        
        weekday_averages = {}
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, day in enumerate(weekdays):
            if weekday_moods[i]:
                weekday_averages[day] = sum(weekday_moods[i]) / len(weekday_moods[i])
            else:
                weekday_averages[day] = None
        
        # Find most common tags
        all_tags = []
        for entry in self.entries:
            all_tags.extend(entry.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'weekday_averages': weekday_averages,
            'common_tags': common_tags,
            'total_entries': len(self.entries)
        }
    
    def export_data(self) -> str:
        """Export all entries as JSON string"""
        return json.dumps([entry.to_dict() for entry in self.entries], indent=2)
    
    def import_data(self, json_data: str) -> bool:
        """Import entries from JSON string"""
        try:
            data = json.loads(json_data)
            imported_entries = [MoodEntry.from_dict(entry_data) for entry_data in data]
            self.entries.extend(imported_entries)
            return True
        except Exception as e:
            print(f"Error importing data: {e}")
            return False
