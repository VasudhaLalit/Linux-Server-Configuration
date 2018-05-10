from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    picture = Column(String(250))


class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    dept_name = Column(String(30), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    designation = Column(String(50), nullable=False)
    salary = Column(String(10))
    archival_flag = Column(String(1))
    dept_id = Column(Integer, ForeignKey('department.id'))
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime)
    desk_ph = Column(String(12))
    emp_email = Column(String(50))
    city_state = Column(String(50))
    reporting_manager = Column(String(50))
    updated_on = Column(DateTime, onupdate=func.now())
    department = relationship(Department)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return{
            'name': self.name,
            'designation': self.designation,
            'reporting manager': self.reporting_manager,
        }


engine = create_engine('postgresql://empcat:empcat@localhost/emp_catalog')
Base.metadata.create_all(engine)
