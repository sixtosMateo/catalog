from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalogitems.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()


User1 = User(name = "adilene constante", email = "adiconst@gmail.com")
session.add(User1)
session.commit()


category1 = Category(name = "Boxing", user_id=1)
session.add(category1)
session.commit()

Item1 = Item(name = "gloves", user_id = 1, category= category1 ,description =
"Gloves are custom to be light but insert pain when hit contacts opponent.")
session.add(Item1)
session.commit()

Item2 = Item(name = "shorts", user_id = 1, category= category1 ,description =
"These shorts determines where the opponent is allowed to hit you or not")
session.add(Item2)
session.commit()


Item3 = Item(name = "shoes", user_id = 1, category= category1 ,description =
"These shoes gives fighters the grip in the area and flexibility to move")
session.add(Item3)
session.commit()


category2 = Category(name = "Soccer", user_id=1)
session.add(category2)
session.commit()

Item1 = Item(name = "gloves", user_id = 1, category= category2 ,description =
"This gloves are tended for goal keepers to have better grip to grab the ball.")
session.add(Item1)
session.commit()

Item2 = Item(name = "cleats", user_id = 1, category= category2 ,description =
"Cleats allow soccer players to maneuver with the soccer ball")
session.add(Item2)
session.commit()


Item3 = Item(name = "ball", user_id = 1, category= category2 ,description =
"The soccer ball has to be light and the size of 4")
session.add(Item3)
session.commit()


category3 = Category(name = "Baseball", user_id=1)
session.add(category3)
session.commit()

Item1 = Item(name = "gloves", user_id = 1, category= category3 ,description =
"Players only need one glove with padding to surpress the impact of the ball")
session.add(Item1)
session.commit()

Item2 = Item(name = "bat", user_id = 1, category= category3 ,description =
"Players need to follow the bat regulations to be fair with everyone else")
session.add(Item2)
session.commit()


Item3 = Item(name = "helmet", user_id = 1, category= category3 ,description =
"The helmet prevents players from getting hit with the ball on the head ")
session.add(Item3)
session.commit()



category4 = Category(name = "Football", user_id=1)
session.add(category4)
session.commit()

Item1 = Item(name = "football", user_id = 1, category= category4 ,description =
"The ball is egg shape to be thrown and catch more efficiently")
session.add(Item1)
session.commit()

Item2 = Item(name = "shoulder pads", user_id = 1, category= category4 ,description =
"Prevents players from injury from contact of other players")
session.add(Item2)
session.commit()


Item3 = Item(name = "helmet", user_id = 1, category= category4 ,description =
"The helmet prevents players from getting hit on the head ")
session.add(Item3)
session.commit()
