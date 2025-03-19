import sqlite3

class MLModel:
    def process_log(self, log):
        with sqlite3.connect('data/training.db') as conn:
            cursor = conn.cursor()
            # Check for exact match
            cursor.execute('SELECT tags, status FROM training WHERE level=? AND message_pattern=?',
                          (log['level'], log['message']))
            result = cursor.fetchone()
            if result:
                return {
                    'timestamp': log['timestamp'], 'level': log['level'], 'message': log['message'],
                    'status': 'success',  # Successfully matched training data
                    'prediction': {'status': result[1], 'confidence': 100, 'tags': result[0].split(',')}
                }
            # Check for pattern match by level
            cursor.execute('SELECT tags, status FROM training WHERE level=? AND ? LIKE "%" || message_pattern || "%"',
                          (log['level'], log['message']))
            result = cursor.fetchone()
            if result:
                return {
                    'timestamp': log['timestamp'], 'level': log['level'], 'message': log['message'],
                    'status': 'success',  # Successfully matched pattern
                    'prediction': {'status': result[1], 'confidence': 90, 'tags': result[0].split(',')}
                }
        # Default prediction if no training data matches
        confidence = 80 if 'INFO' in log['level'] else 95
        status = 'Good' if log['level'] == 'INFO' else 'Issue'
        tags = ['Backup'] if 'started' in log['message'] else ['Error']
        return {
            'timestamp': log['timestamp'], 'level': log['level'], 'message': log['message'],
            'status': 'pending',  # Not trained, needs review
            'prediction': {'status': status, 'confidence': confidence, 'tags': tags}
        }

    def train(self, log, tags, status):
        return {
            'timestamp': log['timestamp'], 'level': log['level'], 'message': log['message'],
            'status': 'success',  # Trained logs are successful
            'prediction': {'status': status, 'confidence': 100, 'tags': tags}
        }