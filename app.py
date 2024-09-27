from flask import Flask, url_for, flash, render_template, request, redirect
from sqlalchemy import and_
from flask_migrate import Migrate  # Import Flask-Migrate
from models import db, Sponsor, Influencer, Campaign_Data, Private_Requests , Public_Requests , Completed_Campaigns,Ongoing_Ads,Admin
from datetime import datetime
import os
from dotenv import load_dotenv



app = Flask(__name__)
app.secret_key = '123456789'

# Configuration for the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'  # Example using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)
load_dotenv()

# Initialize Flask-Migrate with the app and db
migrate = Migrate(app, db)

@app.route('/')
def index():
    db.create_all()
    return redirect(url_for('login'))

@app.route('/admin/login_admin' , methods = ['GET','POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        passkey = request.form.get('password')
        user = (Admin.query.filter_by(admin_email=email).first())
        if(user and user.admin_password == passkey ):
            flash('Login successful!')
            return redirect(url_for('admin_dashboard',user_id=user.admin_id))
        else:
            flash('UNAUTHORISED')
            return render_template('admin_login.html')

    return render_template('admin_login.html')

@app.route('/admin/dashboard/sponsor/blacklist/<int:user_id>/<int:campaign_id>',methods=['GET','POST'])
def blacklist_campaign(user_id , campaign_id):
    campaign_bl = Campaign_Data.query.get(campaign_id)
    if campaign_bl:
        campaign_bl.blacklisted=1
        db.session.commit()
    return redirect(request.referrer)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Perform logout logic here, such as clearing user session data
    # Example: session.pop('user_id', None) or similar logic

    return redirect(url_for('index'))  # Redirect to the index route

@app.route('/admin/dashboard/sponsor/whitelist/<int:user_id>/<int:campaign_id>', methods=['GET', 'POST'])
def whitelist_campaign(user_id, campaign_id):
    campaign_bl = Campaign_Data.query.get(campaign_id)
    if campaign_bl:
        campaign_bl.blacklisted=0
        db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/dashboard/sponsor/blacklist/<int:user_id>/', methods=['GET', 'POST'])
def Spons_Blacklist(user_id):
    sponsor = Sponsor.query.get(user_id)
    if sponsor:
        sponsor.blacklisted = 1
        db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/dashboard/influencer/blacklist/<int:user_id>/', methods=['GET', 'POST'])
def Influ_Blacklist(user_id):
    influencer = Influencer.query.get(user_id)
    if influencer:
        influencer.blacklisted = 1
        db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/dashboard/sponsor/whitelist/<int:user_id>/', methods=['GET', 'POST'])
def Spons_Whitelist(user_id):
    sponsor = Sponsor.query.get(user_id)
    if sponsor:
        sponsor.blacklisted = 0
        db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/dashboard/influencer/whitelist/<int:user_id>/', methods=['GET', 'POST'])
def Influ_Whitelist(user_id):
    influencer = Influencer.query.get(user_id)
    if influencer:
        influencer.blacklisted = 0
        db.session.commit()
    return redirect(request.referrer)


@app.route('/admin/dashboard/<int:user_id>', methods=['GET', 'POST'])
def admin_dashboard(user_id):
    admin = Admin.query.get(user_id)
    sponsors = Sponsor.query.all()
    influencers = Influencer.query.all()
    return render_template('admin_dashboard.html',
                           admin=admin, sponsors=sponsors, influencers=influencers, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = (Sponsor.query.filter_by(email=email).first() or Influencer.query.filter_by(email=email).first())

        if user and user.password == password:
            flash('Login successful!')
            if user.blacklisted == 0:
                if isinstance(user, Sponsor):
                    return redirect(url_for('sponsor', user_id=user.id))
                elif isinstance(user, Influencer):
                    return redirect(url_for('influencer', user_id=user.id))
                else:
                    error = 'USER TYPE NOT SPECIFIED , ERROR 404'
            else:
                error = 'BLACKLISTED USER , CONTACT admin@admin.com for whitelisting process'
        elif user and user.password != password:
            error = 'Incorrect Password, Please Try again'
        else:
            error = 'Account Does Not exist'
    return render_template('index.html', error=error)

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    error = ''
    new_user = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usertype = request.form['usertype']
        name = request.form['Name']
        industry = None
        company_name = None
        followers = None
        niche1 = None
        niche2 = None
        niche3 = None
        print("Received form data:", request.form)  # Add this line to print the form data

        if usertype == 'Sponsor':
            company_name = request.form['Company']
            industry = request.form['Industry']
        elif usertype == 'Influencer':
            followers = request.form['Followers']
            niche1 = request.form['niche1']
            niche2 = request.form['niche2']
            niche3 = request.form['niche3']

        existing_user = Sponsor.query.filter_by(email=email).first() or Influencer.query.filter_by(email=email).first()
        if existing_user is None:
            if usertype == 'Sponsor':
                new_user = Sponsor(email=email, password=password, name=name, company_name=company_name, industry=industry,blacklisted=0)
            elif usertype == 'Influencer':
                new_user = Influencer(email=email, password=password, name=name, followers=followers,niche1=niche1,niche2=niche2,niche3=niche3,blacklisted=0)
            db.session.add(new_user)
            try:
                db.session.commit()
                flash('Sign up successful! Please log in.')
                return redirect(url_for('login'))
            except Exception as e:
                error = 'Error committing changes to database: {}'.format(e)
        else:
            error = 'Email already registered'

    return render_template('signup.html', error=error)


@app.route('/sponsor/<int:user_id>/dashboard', methods=['GET', 'POST'])
def sponsor(user_id):
    sponsor1 = Sponsor.query.get(user_id)
    if not sponsor1:
        flash('User not found!')
        return redirect(url_for('login'))


    public_requests_notaccepted = Public_Requests.query.filter(
        and_(
            Public_Requests.sponsor_id == user_id,
            Public_Requests.influencer_email.is_(None)
        )
    ).all()
    update_progress()

    #print(f"Pending campaigns: {pending_campaigns}")  # Debug print

    # Query for ongoing campaigns
    ongoing_campaigns = Campaign_Data.query.filter(
        and_(
            Campaign_Data.sponsor_id == user_id,
            Campaign_Data.progress<100
        )
    ).all()


    private_requests_notaccepted = Private_Requests.query.filter(
        and_(
            Private_Requests.sponsor_id == user_id,
            Private_Requests.accepted == 0
        )
    ).all()
    #print(f"Private requests: {private_requests}")  # Debug print

    return render_template('sponsor.html',
                           sponsor1=sponsor1,
                           user_id=user_id,
                           ongoing_campaigns=ongoing_campaigns,
                           ads_pending = public_requests_notaccepted,
                           private_requests=private_requests_notaccepted)


@app.route('/sponsor/<int:user_id>/campaigns/find/<int:influencer_id>/private_request', methods=['GET', 'POST'])
def priv_request(user_id, influencer_id):
    campaigns = Campaign_Data.query.filter_by(sponsor_id=user_id).all()
    current_datetime = datetime.now()
    date_posted = current_datetime.date()
    influencer_prof = Influencer.query.get_or_404(influencer_id)
    if request.method == 'POST':
        sponsor_id=user_id
        campaign_id = request.form['campaign_id']
        campaign_title = request.form.get('campaignTitle')
        campaign_description = request.form.get('campaignDescription')
        niche = request.form.get('niche')
        influencer_email=influencer_prof.email
        publ_id = 0

        budget = request.form.get('budget')

        progress = 0

        new_private_request = Private_Requests(ad_title=campaign_title, requirements=campaign_description,
                                              niche=niche, date_posted=date_posted, budget=budget,
                                              influencer_email=influencer_email,
                                              sponsor_id=sponsor_id, accepted=0, campaign_id=campaign_id,publ_id=publ_id)
        db.session.add(new_private_request)
        db.session.commit()
        return redirect(url_for('find_influencer',user_id=user_id))

        # Other form handling logic
    return render_template('priv_request_form.html', user_id=user_id, campaigns=campaigns, influencer_id=influencer_id)


@app.route('/influencer/<int:user_id>/dashboard/<int:ongoing_ad_id>/mark_complete', methods=['POST'])
def mark_complete(user_id, ongoing_ad_id):
    influencer = Influencer.query.filter_by(id=user_id).first()
    if not influencer:
        # Handle the case where the influencer does not exist
        return redirect(request.referrer)

    ongoing_ad = Ongoing_Ads.query.filter(
        and_(
            Ongoing_Ads.ad_id == ongoing_ad_id,
            Ongoing_Ads.influencer_email == influencer.email
        )
    ).first()

    if ongoing_ad:
        ongoing_ad.completed = 1
        db.session.commit()

    return redirect(request.referrer)

@app.route('/influencer/<int:user_id>/dashboard', methods=['GET', 'POST'])
def influencer(user_id):
    influencer1 = Influencer.query.get(user_id)
    influencer_email = influencer1.email
    if not influencer1:
        flash('User not found!')
        return redirect(url_for('login'))
    ongoing_ads = Ongoing_Ads.query.filter(
        and_(
            Ongoing_Ads.influencer_email == influencer_email
        )
    ).all()
    pending = Private_Requests.query.filter(
        Private_Requests.influencer_email == influencer_email,
        Private_Requests.accepted == 0
    ).all()
    return render_template('influencer.html',influencer1=influencer1,user_id=user_id,pending=pending,ongoing_ads=ongoing_ads)

def get_campaign_data(user_id):
    ongoing_campaigns = Campaign_Data.query.filter(
        and_(
            Campaign_Data.sponsor_id == user_id,
            Campaign_Data.progress < 100
        )
    ).all()
    completed_campaigns = Completed_Campaigns.query.filter(
        Completed_Campaigns.sponsor_id == user_id
    ).all()
    update_progress()
    return ongoing_campaigns, completed_campaigns

@app.route('/admin/sponsor/<int:user_id>/view', methods=['GET', 'POST'])
def getdetails(user_id):
    ongoing_campaigns, completed_campaigns = get_campaign_data(user_id)
    path_admin = render_details_Admin(request.path)
    return render_template('campaign_page.html', user_id=user_id, ongoing_campaigns=ongoing_campaigns, completed_campaigns=completed_campaigns,path_admin=path_admin)
def render_details_Admin(path):
    if 'admin' in path :
        return True
    else:
        return False




@app.route('/sponsor/<int:user_id>/campaigns/', methods=['GET', 'POST'])
def campaign(user_id):
    path_admin = render_details_Admin(request.path)
    ongoing_campaigns = Campaign_Data.query.filter(
        and_(
            Campaign_Data.sponsor_id == user_id,
            Campaign_Data.progress < 100
        )
    ).all()
    completed_campaigns = Completed_Campaigns.query.filter(
        Completed_Campaigns.sponsor_id == user_id
    ).all()

    update_progress()

    # sponsor Campaign Page
    return render_template('campaign_page.html', user_id=user_id, ongoing_campaigns=ongoing_campaigns, completed_campaigns=completed_campaigns,path_admin = path_admin)


def update_progress():
    # Define weights (adjust these as needed)
    weight_ongoing = 0.4
    weight_private = 0.3
    weight_public = 0.3

    # Fetch all campaigns with their related ongoing ads, private requests, and public requests
    campaigns = (
        db.session.query(Campaign_Data)
        .outerjoin(Ongoing_Ads, Campaign_Data.campaign_id == Ongoing_Ads.campaign_id)
        .outerjoin(Private_Requests, Campaign_Data.campaign_id == Private_Requests.campaign_id)
        .outerjoin(Public_Requests, Campaign_Data.campaign_id == Public_Requests.campaign_id)
        .group_by(Campaign_Data.campaign_id)
        .all()
    )

    for campaign in campaigns:
        # Calculate counts directly from the joined queries
        total_ongoing_ads = (
            db.session.query(db.func.count(Ongoing_Ads.ad_id))
            .filter(Ongoing_Ads.campaign_id == campaign.campaign_id, Ongoing_Ads.completed == 0)
            .scalar() or 0
        )
        ongoing_ads_completed = (
            db.session.query(db.func.count(Ongoing_Ads.ad_id))
            .filter(Ongoing_Ads.campaign_id == campaign.campaign_id, Ongoing_Ads.completed == 1)
            .scalar() or 0
        )
        total_private_requests = (
            db.session.query(db.func.count(Private_Requests.priv_id))
            .filter(Private_Requests.campaign_id == campaign.campaign_id, Private_Requests.publ_id == 0)
            .scalar() or 0
        )
        total_public_requests = (
            db.session.query(db.func.count(Public_Requests.publ_id))
            .filter(Public_Requests.campaign_id == campaign.campaign_id)
            .scalar() or 0
        )

        # Debugging: print the values to verify correctness
        print("Campaign ID: {}".format(campaign.campaign_id))
        print("Total Ongoing Ads: {}".format(total_ongoing_ads))
        print("Ongoing Ads Completed: {}".format(ongoing_ads_completed))
        print("Total Private Requests: {}".format(total_private_requests))
        print("Total Public Requests: {}".format(total_public_requests))

        # Calculate weighted progress
        total_requests = total_ongoing_ads + total_public_requests + total_private_requests
        if total_requests > 0:
            progress_ongoing = (ongoing_ads_completed / total_ongoing_ads) if total_ongoing_ads > 0 else 0
            progress_private = (total_private_requests / (total_private_requests + total_public_requests)) if (total_private_requests + total_public_requests) > 0 else 0
            progress_public = (total_public_requests / (total_private_requests + total_public_requests)) if (total_private_requests + total_public_requests) > 0 else 0

            weighted_progress = (
                (progress_ongoing * weight_ongoing +
                 progress_private * weight_private +
                 progress_public * weight_public)
            ) * 100

            # Set maximum progress to 99.9
            if weighted_progress > 99.9:
                weighted_progress = 99.9

            campaign.progress = int(weighted_progress)
        else:
            campaign.progress = 0

        # Debugging: print the final progress
        print("Calculated Progress: {}".format(campaign.progress))

    db.session.commit()



@app.route('/sponsor/<int:user_id>/campaigns/<int:campaign_id>/<string:campaign_type>/add_advert', methods=['GET', 'POST'])
def add_adv(user_id, campaign_type,campaign_id):
    if request.method == 'POST':
        # Handle form submission based on campaign_type
        current_datetime = datetime.now()
        unique_number = int(current_datetime.strftime("%Y%m%d%H%M%S"))
        date_posted = current_datetime.date()
        influencer = None
        sponsor_id = user_id
        if campaign_type == 'public':
            campaign_title = request.form.get('campaignTitle')
            campaign_description = request.form.get('campaignDescription')
            niche = request.form.get('niche')

            budget = request.form.get('budget')
            progress = 0

            new_pending_request = Public_Requests(publ_id =unique_number, ad_title=campaign_title, requirements=campaign_description,
                                                niche=niche, date_posted=date_posted, budget=budget, influencer_email=influencer,
                                                sponsor_id=sponsor_id,accepted=0,campaign_id=campaign_id)
            db.session.add(new_pending_request)
            db.session.commit()

        else:
            # Handle other campaign types if needed
            pass

        return redirect(url_for('sponsor', user_id=user_id))  # Replace with your sponsor page endpoint

    return render_template('add_req.html', user_id=user_id, campaign_type=campaign_type,campaign_id=campaign_id)


@app.route('/sponsor/<int:user_id>/campaigns/private/<int:ad_id>/accept_negotiation', methods=['GET', 'POST'])
def accept_negotiation(user_id, ad_id):
    try:
        # Fetch and update the private request
        ad_acc = Private_Requests.query.get_or_404(ad_id)
        ad_acc.accepted = 1
        ad_acc.budget = ad_acc.negotiation_amt
        public_ad_id = ad_acc.publ_id

        current_datetime = datetime.now()
        date_posted = current_datetime.date()

        # Create an ongoing ad entry
        ongoing_ad = Ongoing_Ads(
            publ_id=public_ad_id,
            date_accepted=date_posted,
            campaign_id=ad_acc.campaign_id,
            sponsor_id=ad_acc.sponsor_id,
            ad_title=ad_acc.ad_title,
            requirements=ad_acc.requirements,
            influencer_email=ad_acc.influencer_email,
            budget_ad=ad_acc.budget,
            completed=0,
            blacklisted=0
        )

        # Delete the corresponding public ad entry if it exists
        del_ad = Public_Requests.query.get(public_ad_id)
        if del_ad:
            db.session.delete(del_ad)

        # Delete all private requests with the same public ID that are not accepted
        Private_Requests.query.filter_by(publ_id=public_ad_id).filter(Private_Requests.accepted != 1).delete(synchronize_session=False)

        # Add the new ongoing ad entry and commit
        db.session.add(ongoing_ad)
        db.session.commit()

        flash('Negotiation accepted and advertisement moved to ongoing ads.', 'success')
    except Exception as e:
        db.session.rollback() # Debugging: print the error
        flash('An error occurred while accepting the negotiation.', 'danger')
        return redirect(request.referrer)

    return redirect(request.referrer)


@app.route('/influencer/<int:user_id>/campaigns/<string:ad_type>/<int:ad_id>/negotiate', methods=['GET', 'POST'])
def push_negotiation(user_id, ad_type, ad_id):
    if request.method == 'POST':
        negotiation_amount = request.form.get('negotiationAmount')
        if not negotiation_amount:
            flash('Negotiation amount is required.', 'danger')
            return redirect(url_for('influencer', user_id=user_id))

        if ad_type == 'private':
            ad_acc = Private_Requests.query.filter_by(priv_id=ad_id).first()
            if ad_acc:
                ad_acc.negotiation_amt = negotiation_amount
                try:
                    db.session.commit()
                    flash('Negotiation amount submitted successfully.', 'success')
                except Exception as e:
                    db.session.rollback()
            else:
                flash('Campaign not found.', 'danger')
        else:
            ad_acc = Public_Requests.query.filter_by(publ_id=ad_id).first()
            if ad_acc:
                influencer = Influencer.query.get_or_404(user_id)
                current_datetime = datetime.now()
                date_posted = current_datetime.date()
                public_ad_req = Private_Requests(
                    publ_id=ad_acc.publ_id,
                    date_posted=date_posted,
                    campaign_id=ad_acc.campaign_id,
                    sponsor_id=ad_acc.sponsor_id,
                    ad_title=ad_acc.ad_title,
                    requirements=ad_acc.requirements,
                    niche=ad_acc.niche,
                    influencer_email=influencer.email,
                    budget=ad_acc.budget,
                    negotiation_amt=negotiation_amount,
                    accepted=0
                )
                db.session.add(public_ad_req)
                try:
                    db.session.commit()
                    flash('Negotiation amount submitted successfully.', 'success')
                except Exception as e:
                    db.session.rollback()
            else:
                flash('Campaign not found.', 'danger')

        return redirect(url_for('influencer', user_id=user_id))

    return redirect(url_for('influencer', user_id=user_id))




@app.route('/update_campaign/<int:user_id>/<int:campaign_id>', methods=['POST'])
def update_campaign(user_id, campaign_id):
    campaign = Campaign_Data.query.get_or_404(campaign_id)

    if request.method == 'POST':
        # Retrieve form data
        campaign.campaign_title = request.form['title']
        campaign.campaign_description = request.form['description']
        campaign.budget = request.form['budget']

        # Update the campaign in the database
        try:
            db.session.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(request.referrer)
        except Exception as e:
            db.session.rollback()
            return redirect(request.referrer)


@app.route('/sponsor/<int:user_id>/campaigns/<int:campaign_id>/delete_campaign', methods=['GET','POST'])
def delete_campaign(user_id, campaign_id):

        # Fetch the campaign or return a 404 if not found
        campaign = Campaign_Data.query.get_or_404(campaign_id)

        current_datetime = datetime.now()
        date_posted = current_datetime.date()

        # Create a completed campaign entry
        completed_campaign = Completed_Campaigns(
            date_start=campaign.date_start,
            date_end=date_posted,  # Adjust if needed
            sponsor_id=campaign.sponsor_id,
            campaign_title=campaign.campaign_title,
            campaign_description=campaign.campaign_description,
            niche=campaign.niche,
            influencer_email=None,
            budget=campaign.budget,
            progress=100
        )
        db.session.add(completed_campaign)

        # Update progress for the campaign
        db.session.delete(campaign)

        # Mark ongoing ads as completed
        ongoing_ads = Ongoing_Ads.query.filter_by(campaign_id=campaign_id).all()
        for ad in ongoing_ads:
            ad.completed = 1

        # Delete pending public requests
        ads_pending = Public_Requests.query.filter(
            and_(
                Public_Requests.sponsor_id == user_id,
                Public_Requests.influencer_email.is_(None)
            )
        ).all()
        for ad in ads_pending:
            db.session.delete(ad)

        # Delete unaccepted private requests
        private_requests = Private_Requests.query.filter(
            and_(
                Private_Requests.sponsor_id == user_id,
                Private_Requests.accepted == 0
            )
        ).all()
        for requests in private_requests:
            db.session.delete(requests)

        # Commit all changes to the database
        db.session.commit()

        # Redirect to the sponsor's page
        return redirect(request.referrer)




@app.route('/influencer/<int:user_id>/find', methods=['GET', 'POST'])
def find_adreq(user_id):
    influencer = Influencer.query.get(user_id)
    if influencer is not None:
        influencer_niche = {influencer.niche1, influencer.niche2, influencer.niche3}
    else:
        return redirect(url_for("login"))  # or handle the None case appropriately
    influencer_email = influencer.email

    # Fetch all public requests
    pub_req = Public_Requests.query.all()

    # Fetch all private requests by the influencer
    private_requests = Private_Requests.query.filter_by(influencer_email=influencer_email).all()

    # Get the titles of private requests
    private_request_titles = {req.publ_id for req in private_requests}

    # Filter public requests that do not have private requests by the influencer
    filtered_pub_req = [req for req in pub_req if req.publ_id not in private_request_titles]

    # Separate campaigns based on user niches
    matching_adreq = [req for req in filtered_pub_req if req.niche in influencer_niche]
    non_matching_adreq = [req for req in filtered_pub_req if req.niche not in influencer_niche]

    sorted_adreq = matching_adreq + non_matching_adreq

    return render_template('find_adreq.html', user_id=user_id, campaigns=sorted_adreq)


@app.route('/influencer/<int:user_id>/private/<int:ad_id>/accept_request',methods=['GET','POST'])
def accept_request(user_id,ad_id):
    ad_acc = Private_Requests.query.get_or_404(ad_id)
    ad_acc.negotiation_amt = ad_acc.budget
    current_datetime = datetime.now()
    ad_acc.accepted = 1
    date_posted = current_datetime.date()
    ongoing_ad = Ongoing_Ads(
        publ_id = 0,
        date_accepted=date_posted,
        campaign_id=ad_acc.campaign_id,
        sponsor_id=ad_acc.sponsor_id,
        ad_title=ad_acc.ad_title,
        requirements=ad_acc.requirements,
        influencer_email=ad_acc.influencer_email,
        budget_ad=ad_acc.budget,
        completed=0,blacklisted=0
    )

    db.session.add(ongoing_ad)
    db.session.commit()

    return redirect(url_for('influencer', user_id=user_id))

@app.route('/influencer/<int:user_id>/public/<int:ad_id>/request_ad',methods=['GET','POST'])
def Request_ad(user_id,ad_id):
    ad_acc = Public_Requests.query.get_or_404(ad_id)
    influencer = Influencer.query.get_or_404(user_id)
    current_datetime = datetime.now()
    unique_number = int(current_datetime.strftime("%Y%m%d%H%M%S"))
    date_posted = current_datetime.date()
    public_ad_req = Private_Requests(
        publ_id=ad_acc.publ_id,
        date_posted=date_posted,
        campaign_id=ad_acc.campaign_id,
        sponsor_id=ad_acc.sponsor_id,
        ad_title=ad_acc.ad_title,
        requirements=ad_acc.requirements,
        niche = ad_acc.niche,
        influencer_email=influencer.email,
        budget=ad_acc.budget,
        negotiation_amt = ad_acc.budget,
        accepted=0
    )

    db.session.add(public_ad_req)
    db.session.commit()

    return redirect(url_for('find_adreq', user_id=user_id))



@app.route('/sponsor/<int:user_id>/campaigns/<string:campaign_type>/<int:ad_id>/delete_campaign', methods=['GET', 'POST'])
def delete_adreq_sponsor(user_id, campaign_type, ad_id):
    return delete_adreq_common(user_id, campaign_type, ad_id, 'sponsor')

@app.route('/influencer/<int:user_id>/<string:campaign_type>/<int:ad_id>/delete_campaign', methods=['GET', 'POST'])
def delete_adreq_influencer(user_id, campaign_type, ad_id):
    return delete_adreq_common(user_id, campaign_type, ad_id, 'influencer')

def delete_adreq_common(user_id, campaign_type, ad_id, endpoint):
    if campaign_type == 'public':
        ad_del = Public_Requests.query.get_or_404(ad_id)
    elif campaign_type == 'private':
        ad_del = Private_Requests.query.get_or_404(ad_id)
    else:
        return redirect(request.referrer)

    db.session.delete(ad_del)
    db.session.commit()

    if endpoint == 'sponsor':
        return redirect(url_for('sponsor', user_id=user_id))
    else:
        return redirect(url_for('influencer', user_id=user_id))

@app.route('/sponsor/<int:user_id>/stats', methods=['GET', 'POST'])
@app.route('/influencer/<int:user_id>/stats', methods=['GET', 'POST'])
def display_stats(user_id):
    return render_template('stats.html', user_id=user_id)

@app.route('/sponsor/<int:user_id>/campaigns/add_campaign', methods=['GET', 'POST'])
def add_campaign(user_id):
    if request.method == 'POST':
        # Handle form submission based on campaign_type
        current_datetime = datetime.now()
        date_posted = current_datetime.date()
        sponsor_id = user_id
        campaign_title = request.form.get('campaignTitle')
        campaign_description = request.form.get('campaignDescription')
        niche = request.form.get('niche')
        budget = request.form.get('budget')
        new_pending_request = Campaign_Data(campaign_title=campaign_title,
                                               campaign_description=campaign_description,
                                               niche=niche, budget=budget,
                                               sponsor_id=sponsor_id, date_start=date_posted,progress=0,blacklisted=0)
        db.session.add(new_pending_request)
        db.session.commit()
        return redirect(url_for('campaign', user_id=user_id))  # Replace with your sponsor page endpoint

    return render_template('add_campaign.html', user_id=user_id)

def getview(user_id,campaign_id):
    ongoing_campaign = Campaign_Data.query.get_or_404(campaign_id)
    ongoing_ads = Ongoing_Ads.query.filter(
        and_(
            Ongoing_Ads.campaign_id == campaign_id
        )
    ).all()
    ads_pending = Public_Requests.query.filter(
        and_(
            Public_Requests.sponsor_id == user_id,
            Public_Requests.influencer_email.is_(None)
        )
    ).all()

    private_requests = Private_Requests.query.filter(
        and_(
            Private_Requests.sponsor_id == user_id,
            Private_Requests.accepted == 0
        )
    ).all()

    return ongoing_campaign , ongoing_ads , ads_pending , private_requests

@app.route('/admin/dashboard/campaign/<int:user_id>/<int:campaign_id>/view', methods=['GET','POST'])
def view_campaign_admin(user_id,campaign_id):
    ongoing_campaign , ongoing_ads , ads_pending, private_requests = getview(user_id, campaign_id)
    return render_template('view.html', user_id=user_id,ongoing_campaigns=ongoing_campaign,ongoing_ads=ongoing_ads,ads_pending=ads_pending,private_requests=private_requests)



@app.route('/sponsor/<int:user_id>/campaign/<int:campaign_id>/view' , methods = ['GET','POST'])
def view_campaign(user_id,campaign_id):
    ongoing_campaigns = Campaign_Data.query.get_or_404(campaign_id)
    ongoing_ads = Ongoing_Ads.query.filter(
        and_(
            Ongoing_Ads.campaign_id == campaign_id
        )
    ).all()
    ads_pending = Public_Requests.query.filter(
        and_(
            Public_Requests.sponsor_id == user_id,
            Public_Requests.influencer_email.is_(None)
        )
    ).all()


    private_requests = Private_Requests.query.filter(
        and_(
            Private_Requests.sponsor_id == user_id,
            Private_Requests.accepted == 0
        )
    ).all()


    return render_template('view.html', user_id=user_id,ongoing_campaigns=ongoing_campaigns,ongoing_ads=ongoing_ads,ads_pending=ads_pending,private_requests=private_requests)

@app.route('/sponsor/<int:user_id>/find' , methods = ['GET','POST'])
def find_influencer(user_id):
    influencers = Influencer.query.all()
    campaign = Campaign_Data.query.all()
    return render_template('find.html', user_id=user_id,campaign=campaign,influencers=influencers)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
