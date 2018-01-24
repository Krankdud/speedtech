from speeddb import app, db, user_manager
from speeddb.models.user import User
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from faker import Faker

def main():
    fake = Faker()

    user = User(username=fake.user_name(),
                password=user_manager.hash_password(fake.password()),
                active=True)

    tag = Tag(name='test-data')

    db.session.add(user)
    db.session.commit()

    db.session.add(tag)

    for i in range(2000):
        clip = Clip(title=fake.sentence(),
                    description=fake.text(),
                    url='https://www.youtube.com/watch?v=Zxv5rE1TLJg', # Lost Control 2
                    user_id=user.id,
                    tags=[tag])
        db.session.add(clip)

    db.session.commit()

if __name__ == '__main__':
    main()