import os

import pandas as pd
import numpy as np

from flask import Flask, jsonify, render_template
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


#################################################
# Database Setup
#################################################

#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/belly_button_biodiversity.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Samples_Metadata = Base.classes.samples_metadata
Samples = Base.classes.samples
Otu = Base.classes.otu



@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")


@app.route("/names")
def names():
    """Return a list of sample names."""

    # Use Pandas to perform the sql query
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Return a list of the column names (sample names)
    return jsonify(list(df.columns)[2:])


# Creates otu route
# --------------------------------------------------------------------------
@app.route("/otu")
def otu():
    """ Function: Extracts otu list from table
        Parameters: (none)
        Returns: JSON object of otu list """
    otu_descriptions = db.session.query(Otu.lowest_taxonomic_unit_found).all()
    otu_descriptions_list = [x for (x), in otu_descriptions]
    return jsonify(otu_descriptions_list)

# --------------------------------------------------------------------------
# Creates otu descriptions route
# --------------------------------------------------------------------------
@app.route("/otu_descriptions")
def otu_disc():
    """ Function: Extracts otu descriptions list from table
        Parameters: (none)
        Returns: JSON object of otu descriptions """
    otu_descriptions = db.session.query(Otu.otu_id, \
    Otu.lowest_taxonomic_unit_found).all()
    otu_dict = {}
    for row in otu_descriptions:
        otu_dict[row[0]] = row[1]
    return jsonify(otu_dict)



@app.route("/metadata/<sample>")
def sample_metadata(sample):
    """Return the MetaData for a given sample."""
    sel = [
        Samples_Metadata.SAMPLEID,
        Samples_Metadata.ETHNICITY,
        Samples_Metadata.GENDER,
        Samples_Metadata.AGE,
        Samples_Metadata.LOCATION,
        Samples_Metadata.BBTYPE,
        Samples_Metadata.WFREQ,
    ]

    sample_name = sample.replace("BB_", "")
    results = db.session.query(*sel).filter(Samples_Metadata.SAMPLEID == sample_name).all()

    # Create a dictionary entry for each row of metadata information
    sample_metadata = {}
    for result in results:
        sample_metadata["SAMPLEID"] = result[0]
        sample_metadata["ETHNICITY"] = result[1]
        sample_metadata["GENDER"] = result[2]
        sample_metadata["AGE"] = result[3]
        sample_metadata["LOCATION"] = result[4]
        sample_metadata["BBTYPE"] = result[5]
        sample_metadata["WFREQ"] = result[6]

#   print(sample_metadata)
    return jsonify(sample_metadata)

@app.route('/wfreq/<sample>')
def wash_freq(sample):

    sel = [
        Samples_Metadata.SAMPLEID,
        Samples_Metadata.WFREQ,
    ]
    sample_name = sample.replace("BB_", "")
#   results = db.session.query(*sel).filter(Samples_Metadata.sample == sample).all()
    results = db.session.query(Samples_Metadata.WFREQ).\
    filter_by(SAMPLEID = sample_name).all()
    # Create a dictionary entry for each row of metadata information
    wash_freq = {}
    wash_freq = results[0][0]

#   print(wash_freq)
    return jsonify(wash_freq)

@app.route('/samples/<sample>')
def otu_data(sample):
    """ Function: otu data query functionality
        Queries otu table and extracts data for sample
        Parameters: 1 (string) sample ID
        Returns: JSON object of otu data for sample ID """
    sample_query = "Samples." + sample
    result = db.session.query(Samples.otu_id, sample_query).\
    order_by(desc(sample_query)).all()
    otu_ids = [result[x][0] for x in range(len(result))]
    sample_values = [result[x][1] for x in range(len(result))]
    dict_list = [{"otu_ids": otu_ids}, {"sample_values": sample_values}]
    return jsonify(dict_list)



if __name__ == "__main__":
    app.run()
