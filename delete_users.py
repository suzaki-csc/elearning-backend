#!/usr/bin/env python3
"""
Script to delete all users from the database
"""

from src.config.database import SessionLocal
from src.models.user import User

def delete_all_users():
    """Delete all users from the database"""
    # データベースセッションを作成
    db = SessionLocal()
    
    try:
        # 全ユーザーを取得
        users = db.query(User).all()
        user_count = len(users)
        print(f'削除前のユーザー数: {user_count}')
        
        if user_count > 0:
            # 各ユーザーの情報を表示
            print('\n削除対象のユーザー:')
            for user in users:
                print(f'- {user.email} ({user.display_name})')
            
            # 全ユーザーを削除
            db.query(User).delete()
            db.commit()
            print(f'\n✅ {user_count}人のユーザーを削除しました')
        else:
            print('削除するユーザーがありません')
            
        # 削除後の確認
        remaining_users = db.query(User).count()
        print(f'削除後のユーザー数: {remaining_users}')
        
    except Exception as e:
        print(f'❌ エラーが発生しました: {e}')
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_users() 