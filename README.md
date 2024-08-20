# Ascenda's Loyalty Points Marketplace
## Loyalty Points Marketplace
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
