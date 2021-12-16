# VisitPay Take-Home Technical Assessment
The purpose of this take-home assessment is to give us a glimpse into your thought processes and technical ability in the realm of data engineering. As you design and implement your approach, do your best to adhere to the core principles of data engineering and object oriented programming.

**The minimum requirements of the application are:**
* It is able to run on a daily basis which will ingest files previously not consumed
* Only files formatted 'HospitalABC_VisitPay_{type}_[YYYYmmdd_hhmmss].txt' are ingested where type is *Visit*, *Transaction*, or *Procedure*
* Data ingested is ultimately published to a database of your choosing
* Referential integrity is established as a part of the application and exists in the database architecture
 
**Additional aspects to consider:**
* Anomaly detection, logging, monitoring, alerting
* Environments and deployments
* Testing
* Bad data parameterization and handling

**Problem Statement:**
The end goal of this exercise to have built a small and performant ETL application utilizing Python or the Databricks Community Edition that meets the minimum requirements. If appropriate, consider incorporating components from the *Additional aspects to consider* section. Submitting the assessment can be done via any avenue with which you are most comfortable, with a few possible examples being a zipped folder, a git repo, a docker image/compose. In addition to the application itself, please include a markdown containing a brief description of your application as well as instructions to the user on how to invoke the application.

For any specifics not explicitly stated in these instructions, feel free to make your own assumptions and document them in your application description. If you encounter an impediment and are unable to circumvent with a set of assumptions, please reach out to Mike McDonnell at mmcdonnell@visitpay.com