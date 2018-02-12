from speeddb import create_app, db
from speeddb.models.user import User
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
import speeddb.search as search
from faker import Faker

NUM_OF_ENTRIES = 50000

def main():
    app = create_app()
    app.app_context().push()

    fake = Faker()

    search.create_index(app.config['WHOOSH_INDEX'])

    user = User(username=fake.user_name(),
                password=fake.password(),
                email=fake.email(),
                active=True)
    print('Created user')

    tag = Tag.query.filter_by(name='test-data').first()
    if tag == None:
        tag = Tag(name='test-data')
        db.session.add(tag)

    db.session.add(user)
    db.session.commit()

    print('Creating clips...')
    clips = []
    for i in range(NUM_OF_ENTRIES):
        if i % 1000 == 0:
            print('Clip %d of %d' % (i, NUM_OF_ENTRIES))
        
        clip = Clip(title=fake.sentence(),
                    description=fake.text(),
                    url='https://www.youtube.com/watch?v=Zxv5rE1TLJg', # Lost Control 2
                    user_id=user.id,
                    tags=[tag])
        db.session.add(clip)
        clips.append(clip)

    print('Committing to db')
    db.session.commit()
    print('Adding to search')
    search.add_clips(clips)
    print('Done!')

if __name__ == '__main__':
    main()