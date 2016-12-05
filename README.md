
# sdc-questionnaires
This component provides access to currently active questionnaire response requests.

## Endpoints

The following endpoints are available on this service:

### /questionnaires/[reporting_unit_ref]

*GET* a list of the surveys curretly requested of the specified RU.

*NB* You'll need to provide your JWT token in a *token* header.

This endpoint returns a map of: 

```json
{
  "data": {
    "surveys": [
      " ... list of survey objects ... "
    ],
    "...": "..."
  },
  "token": " ... token ... "
}
```

### /create-questionnaires

*POST* a list of all respondents for a given RU and survey combination.

*NB* You'll need to provide your JWT token in a *token* header.

This endpoint accepts the following message:

```json
{
  "survey_ref": " ... ",
  "survey_period": " ... ",
  "form_type": " ... ",
  "reporting_unit": " ... ",
  "reporting_unit_name": " ... "
}
```

Currently, the survey ID will be set to *SURVEYID* and the state will be set to *LIVE*.

## Links

Try:
 * https://sdc-questionnaire-responses.herokuapp.com

## Setting up

Run the following from a terminal:

```bash
mkvirtualenv -p `which python3.5` sdc-questionnaire-responses
pip install -r requirements.txt
```

## Running it

```bash
workon sdc-questionnaire-responses
python3 app.py
```
