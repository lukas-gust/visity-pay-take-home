CREATE TABLE "Visit" (
	"VisitIdentifier"	INTEGER NOT NULL,
	"GuarantorIdentifier"	INTEGER NOT NULL,
	"AdmitDate"	TEXT NOT NULL,
	"DischargeDate"	TEXT,
	"VisitBalance"	REAL,
	"InsuranceIdentifier"	INTEGER,
	PRIMARY KEY("VisitIdentifier")
);

CREATE TABLE "Procedure" (
	"ProcedureId"	INTEGER NOT NULL,
	"ProcedureDescription"	TEXT NOT NULL,
	PRIMARY KEY("ProcedureId")
);

CREATE TABLE "Transaction" (
	"TransactionIdentifier"	INTEGER NOT NULL,
	"VisitIdentifier"	INTEGER NOT NULL,
	"ProcedureId"	INTEGER NOT NULL,
	"Amount"	Real,
	PRIMARY KEY("TransactionIdentifier"),
	FOREIGN KEY("VisitIdentifier") REFERENCES "Visit"("VisitIdentifier"),
	FOREIGN KEY("ProcedureId") REFERENCES "Procedure"("ProcedureId")
);