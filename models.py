from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Influencer(db.Model):
        __tablename__ = 'influencer'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(120), nullable=False)
        name = db.Column(db.String(150))
        followers = db.Column(db.Integer, nullable=False)
        niche1 = db.Column(db.Text)
        niche2 = db.Column(db.Text)
        niche3 = db.Column(db.Text)
        blacklisted = db.Column(db.Integer, nullable=False)

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(150),nullable = True)
    company_name = db.Column(db.String(150),nullable = True)
    industry = db.Column(db.String(150),nullable = True)
    blacklisted = db.Column(db.Integer, nullable=False)


class Campaign_Data(db.Model):
    __tablename__ = 'campaign'
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_start = db.Column(db.String(100), nullable=False)
    sponsor_id = db.Column(db.Integer, nullable=False)
    campaign_title = db.Column(db.String(150))
    campaign_description = db.Column(db.Text)
    niche = db.Column(db.String(35))
    budget = db.Column(db.Integer)
    progress = db.Column(db.Integer)
    blacklisted = db.Column(db.Integer, nullable=False)

class Private_Requests(db.Model):  #private and not started yet
    __tablename__ = 'priv_requests'
    priv_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    publ_id = db.Column(db.Integer,nullable=False)
    date_posted = db.Column(db.String(100), nullable=False)
    sponsor_id = db.Column(db.Integer, nullable=False)
    campaign_id = db.Column(db.Integer)
    ad_title =  db.Column(db.String(100))
    requirements = db.Column(db.Text , nullable = False)
    niche = db.Column(db.String(100))
    influencer_email = db.Column(db.String(120))
    budget = db.Column(db.Integer)
    accepted = db.Column(db.Integer,nullable = False)
    negotiation_amt = db.Column(db.Integer)

class Public_Requests(db.Model):
    __tablename__ = 'publ_requests'
    publ_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_posted = db.Column(db.String(100), nullable=False)
    sponsor_id = db.Column(db.Integer, nullable=False)
    campaign_id = db.Column(db.Integer)
    ad_title = db.Column(db.String(100))
    requirements = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(100))
    influencer_email = db.Column(db.String(120))
    budget = db.Column(db.Integer)
    accepted = db.Column(db.Integer, nullable=False)


class Ongoing_Ads(db.Model): #Currently Work in Progress in here
    __tablename__ = 'ongoing_ads'
    ad_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    publ_id = db.Column(db.Integer,nullable=False)
    date_accepted = db.Column(db.String(100), nullable=False)
    campaign_id = db.Column(db.Integer,nullable=False)
    sponsor_id = db.Column(db.Integer, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    ad_title = db.Column(db.String(150))
    budget_ad = db.Column(db.Integer,nullable=False)
    influencer_email = db.Column(db.String(120))
    completed  = db.Column(db.Integer)
    blacklisted = db.Column(db.Integer, nullable=False)



class Completed_Campaigns(db.Model):
    __tablename__ = 'completed'
    completed_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_start = db.Column(db.String(100), nullable=False)
    date_end   = db.Column(db.String(100), nullable=False)
    sponsor_id = db.Column(db.Integer, nullable=False)
    campaign_title = db.Column(db.String(150))
    campaign_description = db.Column(db.String(250))
    niche = db.Column(db.String(35))
    influencer_email = db.Column(db.String(120))
    budget = db.Column(db.Integer)
    progress = db.Column(db.Integer)

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_email = db.Column(db.String(120), unique=True, nullable=False)
    admin_password = db.Column(db.String(120), nullable=False)
    name_admin = db.Column(db.String(150))