from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from api.sqlalchemy_db import SessionLocal
from api.sql_models import Todo
from api.models import Todo as DjangoTodo # Import for model finding if needed, but we use sqlalchemy mainly

class Command(BaseCommand):
    help = 'Send email reminders for tasks due soon'

    def handle(self, *args, **kwargs):
        db = SessionLocal()
        try:
            now = datetime.now()
            # Check tasks due today
            today_str = now.strftime('%Y-%m-%d')
            
            # Simple logic: Find unresolved tasks due today where time is passed or approaching
            # Since we store time as string "HH:MM", we can compare lexicographically if format is 24h
            
            todos = db.query(Todo).filter(
                Todo.resolved == False,
                Todo.due_date == today_str,
                Todo.due_time != None,
                Todo.email_sent == False
            ).all()

            for todo in todos:
                # Parse due time
                try:
                    due_hour, due_minute = map(int, todo.due_time.split(':'))
                    due_dt = now.replace(hour=due_hour, minute=due_minute, second=0, microsecond=0)
                    
                    # If due time is in the past OR within next 15 mins
                    diff = due_dt - now
                    # We send if it's already late (diff < 0) or coming up soon (diff < 15 mins)
                    # And don't send if it's due more than 15 mins from now
                    
                    should_send = False
                    if diff.total_seconds() < 900: # 15 mins
                         should_send = True

                    if should_send:
                        self.stdout.write(f"Sending reminder for {todo.title}...")
                        
                        # Get user email - in a real app query User model. 
                        # Here we assume we can fetch it via user_id relationship on Django side or just mock it.
                        # Since SQLTodo doesn't have relation to Auth User easily loaded here without join:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        try:
                            user = User.objects.get(id=todo.user_id)
                            if user.email:
                                send_mail(
                                    subject=f"Reminder: {todo.title} is due!",
                                    message=f"Hi {user.username},\n\nYour task '{todo.title}' is due at {todo.due_time}.\n\nDescription: {todo.description}\n\nGood luck!",
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=[user.email],
                                    fail_silently=False,
                                )
                                todo.email_sent = True
                                db.add(todo)
                                self.stdout.write(self.style.SUCCESS(f"Sent to {user.email}"))
                        except User.DoesNotExist:
                             self.stdout.write(self.style.ERROR(f"User {todo.user_id} not found"))
                        except Exception as e:
                             self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Invalid time format for task {todo.id}: {todo.due_time}"))

            db.commit()
        finally:
            db.close()
