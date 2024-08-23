# Ascenda's Loyalty Points Marketplace
This was part of our SUTD module, Elements of Software Construction, where we selected a project out of the few different projects and develop a software for them. Our team has ultimately chose to work on Ascenda's Loyalty Points Marketplace or TransferConnect. This Github repository is used for TransferConnect, managing API requests from banks and partners. The features/requirements are explained below and exists somewhere in this repository. Feature 6 is not in this repository as it was initially created in a different repository meant to store our parsers and scripts.

### Promotions implementation
To ensure robustness in our promotion system, the promotion rules are stored in our database as a json format with additional information such as name, description, expiry date etc. During the credit request, if the promotion ID is not specified, we will select the best value out of all the promotions. Some of the promotions criteria that we are able to do now.
- Check if user has a certain card
- Check if user has enough spending on certain card
- Check if user has enough spending on certain months on certain cards
We also planned for checking for first time transaction etc but have not implemented that yet due to time constrains and were not able to test it out fully.

When the banks send in a request with the additional information needed, we use that to match the key in the **conditions** then we have a "op" to check for the formula (gt = greater than, lt = less than, eq = equal, lte = less than or equal) etc, and match the "value". The key is usually the card name.

After the condition check, we will then evaluate the points in **points_rule**. The value is an array of different formulas for different points that they are exchanging for. For example, for the first row, if the points that you are exchanging for is below 900, it will add an additional 500 points, thus x + 500. However, if you are exchanging more than 900 points, it will be using the other formula, which is (x-900) * 1.5 + 500, which basically does a 1.5 multipler on additional points after 900 points.

<img width="1139" alt="image" src="https://github.com/user-attachments/assets/a5937ef2-8dd2-4a5e-b5fd-15f055f44130">

### Security implementation
To ensure that the people using the API are authentic users, we decided to use JWT tokens that has a email payload, then subsequently API calls will check the DB if the email exist, and what are the roles. Different API calls require different roles as well to provide a role-based authentication. The credit API calls would require you to be a partner, and then we will automatically select their partner_code so that they cannot randomly change their partner code. Password is hashed with bcrypt so that it cannot easily be decrypted. The JWT token expires in every 1 minute currently so that even if the JWT get stolen, it would have expired and unusable. 
<img width="733" alt="image" src="https://github.com/user-attachments/assets/e4466617-7637-4cd3-b8ae-07f3bab25909">

## Loyalty Points Marketplace (Project description)
There are 3 parties at play here; for which you’ll build 2 apps only:
1. The Bank app
2. The TransferConnect app (where the core logic of points processing exists). 
Note: You do not need to build the Loyalty Program app.

Bank App: Customer facing frontend where a user can submit their points redemption by supplying a loyalty program membership. A simple demo using the different APIs from the TransferConnect App would suffice.

TransferConnect App: The backend-only application is responsible for managing API requests received from banks. Its primary function is to gather credit requests and transmit them to the loyalty program for processing. Communication with the loyalty program occurs through SFTP (Secure File Transfer Protocol) in the form of an accrual file.

Loyalty Program: Fulfills the points to be redeemed in their system by ingesting files you generate and upload to the provisioned SFTP folder. You do not need to build this Loyalty Program app. You can mock the response from the loyalty program by uploading the handback file you generate and have your TransferConnect app ingest it.

### Features of the System 

Ascenda’s Loyalty Points Marketplace is used mostly in the B2B setting. Most customers implement their own UI for the end user’s point’s transfer feature. This can be in the form of a mobile app or as part of the bank’s rewards portal. The main integration mechanism between our customers and Ascenda’s platform would be via real-time API calls. 
The platform should provide the various functionalities: 
- A loyalty programs information endpoint for the display of loyalty program information in the frontend. 
- A loyalty membership validation feature to support validation of end user inputs.
- Accept & process accrual information for loyalty programs on behalf of banks.
- Perform fulfillment (upload accrual file) with the actual loyalty program, integrating with their specific transfer formats (process the handback file).
- Return the credit transaction details when complete and allow querying of credit transfer details.

To demonstrate the usability of this app, you’ll also construct an MVP frontend app to represent a hypothetical “bank client” who’ll be integrating to the core platform you’re providing for.

The UX of the frontend can follow what we’ve demonstrated in Appendix 1.

More details of these features can be found below:
#### Feature 1: Loyalty program API 
Banks rely on the TransferConnect app for the latest information about loyalty programs for display to their end users. Typically, this data is synchronized between systems every day.
The data includes: 

| Attribute | Sample | 
| --- | --- |
| Loyalty Program ID | GOPOINTS |
| Loyalty Program Name | GoJet Points |
| Loyalty Currency Name | GoPoints | 
| Processing time | instant | 
| Description | to edit | 
| Enrollment link | https://www.gojet.com/member/ |
| Terms & conditions link | https://www.gojet.com/aa/about-us/en/gb/terms-and-conditions.html |

#### Feature 2: Membership validation API
This helps the bank customers validate the provided membership number of a given loyalty program. Typically, this is used for form validation, to ensure that the user provides the correct number for a given loyalty program. 
This has to be performant as described in the Non-functional requirements later below. 
We’d like to see ideas around making this feature as performant as possible around various sites globally as much as possible. 

#### Feature 3: Accrual API
This is an API endpoint which receives the accrual request on behalf of the bank. The TransferConnect app will receive the following information.

- Loyalty program ID 
- Member ID 
- Member first & last name 
- Transaction date 
- Unique reference number for reconciliation 
- Amount 
- Any number of additional information as sent by the bank. 
  - E.g. notification phone number or email

The TransferConnect app validates that the member ID sent passes our usual checks and responds with a unique system ID if accepted as well as the status. 

#### Feature 4: Transaction enquiry API
The bank app can query the TransferConnect app for the status of the transaction periodically until completion of the transfer. If it fails, we should show the reason for failure. 
This is used as part of the end user display on their respective bank apps/ site. 
In your bank app frontend, you should show a sample transactions page for the end user to see the status of their program transfer outcome. 
Feature 5: Transfer fulfillments processing
See Appendix 3 for an example of how transfers are fulfilled downstream with loyalty partners. Your solution here should also factor in our file processing policy in the Appendix.

#### Feature 6: Notifications to Bank Client app (ie. your frontend)

We should be able to register on behalf of a given bank’s frontend app, the ability to receive updates on the status of a given transaction.

You can introduce a couple of different samples like: 

- Primary: Notify the bank’s client app that the transfer is done
- Secondary: Notify a registered customer phone number and/ or email that the transaction is done/ failed

As part of this feature, you should demonstrate in your TransferConnect app the ability to register and execute (even reprocess) the different “notification” mechanisms to support day-to-day customer support.

E.g. Re-sending the same email/ SMS notifications for our customers’ reference.

#### Feature 7 (Bonus): Points valuations & Promotions

Underneath the exchange by the customer between the bank loyalty program and the targeted loyalty program is a monetary valuation to the points.

E.g. the bank point might be deemed at 1 cent per point and the loyalty program the same too.

Using the above example, you have a 1:1 points exchange ratio. 

Each customer or membership base has its own set of high-value customers. These high-value customers may include individuals such as frequent travelers who hold Diamond membership with the loyalty program or individuals who have a Black card bank account and spend over 50K annually.

For such customers, we perform targeted offers from time to time with adjusted earn rates depending on the customer segment over here.

Here’s an example. Say typically you can exchange 1 bank point to 1 airline program point. Customers should also have the ability to run offers as follows:
- A Black card holder can exchange for 1 bank point to 1.5 airline program points till the rest of this year on every transaction
- A first time transaction for a given member can also benefit from 1 bank point to 1.5 airline program points too (this is 1-off)

We’d leave it to your imagination to determine what are some of these sample bonuses; The crux is the ability to be able to apply in your TransferConnect app design the ability to give bonus points based on certain attributes of the customer/ loyalty program membership.

(Bonus 2): What if this earn rate was a 1-off and an ongoing period-based spend for the customer on every transaction made? (i.e. earn a 1-off 500 points on first transaction and earn 1000 more points if customer exchange 2000 points in a specific month)
