from faker import Faker

from doc.models import Doc

fake = Faker()

for e in range(300000):
    title = fake.text(50)
    text = fake.text(4000)
    info = fake.text(200)
    warning = fake.text(200)
    d = Doc()
    d.title = title
    d.text = text
    d.info = info
    d.warning = warning
    d.save()
    d.tags.add(fake.word())
    d.tags.add(fake.word())
    d.tags.add(fake.word())
    d.tags.add(fake.word())
    d.tags.add(fake.word())
    d.save()
    d.tag = " ".join(list(d.tags.slugs()))
    d.save()
    print(d.id)
