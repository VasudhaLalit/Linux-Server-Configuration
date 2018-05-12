from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from database_setup import Employee, Base

engine = create_engine('postgresql://empcat:empcat@localhost/emp_catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

new_emp1 = Employee(name='Carson Wentz',
                    designation='11 - Quarterback',
                    salary='10,000,000',
                    archival_flag='N',
                    dept_id='10',
                    start_date=func.now(),
                    desk_ph='428-789-1256',
                    emp_email='carson.wentz@eagles.com',
                    city_state='Phildadelphia/PA',
                    reporting_manager='Doug Pederson',
                    user_id=1)

session.add(new_emp1)
session.commit()

new_emp2 = Employee(name='Nick Foles',
                    designation='12 - Quarterback',
                    salary='10,000,000',
                    archival_flag='N',
                    dept_id='10',
                    start_date=func.now(),
                    desk_ph='428-889-1256',
                    emp_email='nick.foles@eagles.com',
                    city_state='Phildadelphia/PA',
                    reporting_manager='Doug Pederson',
                    user_id=1)

session.add(new_emp2)
session.commit()

new_emp3 = Employee(name='Jay Ajayi',
                    designation='Running Back',
                    salary='10,000,000',
                    archival_flag='N',
                    dept_id='10',
                    start_date=func.now(),
                    desk_ph='428-889-4578',
                    emp_email='jay.ajayi@eagles.com',
                    city_state='Phildadelphia/PA',
                    reporting_manager='Doug Pederson',
                    user_id=1)

session.add(new_emp3)
session.commit()

new_emp4 = Employee(name='Chris Long',
                    designation='Defensive End',
                    salary='10,000,000',
                    archival_flag='N',
                    dept_id='10',
                    start_date=func.now(),
                    desk_ph='478-889-4578',
                    emp_email='chris.long@eagles.com',
                    city_state='Phildadelphia/PA',
                    reporting_manager='Doug Pederson',
                    user_id=1)

session.add(new_emp4)
session.commit()

new_emp5 = Employee(name='Zack Ertz',
                    designation='Tight End',
                    salary='10,000,000',
                    archival_flag='N',
                    dept_id='10',
                    start_date=func.now(),
                    desk_ph='478-889-4578',
                    emp_email='zack.ertz@eagles.com',
                    city_state='Phildadelphia/PA',
                    reporting_manager='Doug Pederson',
                    user_id=1)

session.add(new_emp5)
session.commit()

new_emp6 = Employee(name='Alshon Jeffery',
                    designation='Wide Receiver',
                    salary='10,000,000',
                    archival_flag='N',
                    dept_id='10',
                    start_date=func.now(),
                    desk_ph='478-889-5678',
                    emp_email='Alshon.Jeffery@eagles.com',
                    city_state='Phildadelphia/PA',
                    reporting_manager='Doug Pederson',
                    user_id=1)

session.add(new_emp6)
session.commit()

new_emp7 = Employee(name='Fletcher Cox',
                    designation='Defensive Tackle',
                    salary='10,000,000',
                    archival_flag='N',
                    dept_id='10',
                    start_date=func.now(),
                    desk_ph='478-889-5678',
                    emp_email='Fletcher.cox@eagles.com',
                    city_state='Phildadelphia/PA',
                    reporting_manager='Doug Pederson',
                    user_id=1)

session.add(new_emp7)
session.commit()

print('Employee records added')
