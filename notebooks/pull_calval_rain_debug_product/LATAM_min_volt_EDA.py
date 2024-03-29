#!/usr/bin/env python
# coding: utf-8

# # Fetch and Aggregate Disdrometer Data for Precip Model EDA

# %conda install psycopg2
# %conda install -c anaconda boto3
# %conda install -y -c anaconda sqlalchemy

import boto3
import json
import pandas as pd

from sqlalchemy import create_engine
from utils import df_to_s3, df_from_s3


# # 1. Query to Read from DataBase

# ## Connect to Database

def get_user_db_creds(user: str, environment: str):
    """
    Fetch individual user db credentials from AWS Secretes Manager
    :param user: username that corresponds to secret name of the format "{user}_db_creds"
    :param environment: environment for which to fetch db credentials: "alp", "als", or "alt"
    :return db_info: dictionary that includes  user, password, host, port and db name
    """

    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=f"{user}_db_creds_1")
    secret_db_creds = json.loads(response["SecretString"])
    db_info = {
        "user": secret_db_creds[f"user_{environment}"],
        "password": secret_db_creds[f"password_{environment}"],
        "host": secret_db_creds[f"host_{environment}"],
        "db": secret_db_creds[f"db_{environment}"],
        "port": secret_db_creds[f"port_{environment}"],
    }
    return db_info

def connect_db(dsn: str) -> str:
    cnx = create_engine(dsn)
    return cnx

# ## Starting The Engine...


# retrieve personal tocken from arable secrete Manager
# --may want to change me here
dsn = get_user_db_creds('hong_tang', 'adse')
sqlalchemy_dsn = 'postgresql://{user}:{password}@{host}:{port}/{db}'.format(**dsn)

pg_conn = connect_db(sqlalchemy_dsn)


# ### Define Time window
# --may want to change me here
start = '2022-03-01'
end = '2023-03-01'


# #### Queries for fft by passing devices lists


get_ipython().run_cell_magic('time', '', 'def read_health(cnx, device, begin, end):\n    # schema_raw = \'dsd_raw\'\n    query_template_raw = """\n--may want to change me here\n\nselect \ndate_trunc(\'hour\',h.time) as date\n\t, h.device \n\t, l.country \n\t, min(batt_volt) as min_batt_volt\nfrom device_data_alp.health h \njoin model_data."location" l on h."location" = l.id \nwhere h.device in ({device})\nand h.time >= \'{start}\' and time < \'{end}\'\nGROUP BY 1,2,3\norder by  h.device, date_trunc(\'hour\',h.time)\n\n\n"""\n    #define devices to pull data from\n\n    devices1="\'C002618\', \'C002678\', \'C002693\', \'C002721\', \'C002724\', \'C002746\', \'C002765\', \'C002776\', \'C002779\', \'C002786\', \'C003001\', \'C003002\', \'C003004\', \'C003006\', \'C003007\', \'C003009\', \'C003012\', \'C003021\', \'C003026\', \'C003027\', \'C003030\', \'C003032\', \'C003040\', \'C003041\', \'C003042\', \'C003043\', \'C003046\', \'C003048\', \'C003049\', \'C003051\', \'C003055\', \'C003057\', \'C003059\', \'C003060\', \'C003063\', \'C003064\', \'C003065\', \'C003066\', \'C003069\', \'C003070\', \'C003072\', \'C003073\', \'C003075\', \'C003082\', \'C003083\', \'C003087\', \'C003090\', \'C003091\', \'C003094\', \'C003101\', \'C003113\', \'C003115\', \'C003117\', \'C003118\', \'C003121\', \'C003122\', \'C003129\', \'C003130\', \'C003132\', \'C003134\', \'C003135\', \'C003139\', \'C003142\', \'C003146\', \'C003148\', \'C003151\', \'C003154\', \'C003155\', \'C003157\', \'C003165\', \'C003170\', \'C003171\', \'C003174\', \'C003175\', \'C003176\', \'C003177\', \'C003182\', \'C003185\', \'C003186\', \'C003187\', \'C003188\', \'C003191\', \'C003194\', \'C003197\', \'C003198\', \'C003200\', \'C003201\', \'C003202\', \'C003203\', \'C003204\', \'C003206\', \'C003208\', \'C003213\', \'C003214\', \'C003218\', \'C003221\', \'C003226\', \'C003229\', \'C003231\', \'C003238\', \'C003243\', \'C003248\', \'C003250\', \'C003251\', \'C003256\', \'C003257\', \'C003263\', \'C003264\', \'C003268\', \'C003272\', \'C003275\', \'C003276\', \'C003286\', \'C003290\', \'C003291\', \'C003306\', \'C003313\', \'C003322\', \'C003324\', \'C003332\', \'C003334\', \'C003340\', \'C003343\', \'C003344\', \'C003345\', \'C003352\', \'C003359\', \'C003363\', \'C003365\', \'C003366\', \'C003369\', \'C003371\', \'C003381\', \'C003384\', \'C003389\', \'C003407\', \'C003408\', \'C003409\', \'C003411\', \'C003415\', \'C003419\', \'C003420\', \'C003426\', \'C003427\', \'C003434\', \'C003435\', \'C003453\', \'C003463\', \'C003474\', \'C003477\', \'C003488\', \'C003497\', \'C003601\', \'C003606\', \'C003611\', \'C003612\', \'C003613\', \'C003614\', \'C003618\', \'C003619\', \'C003622\', \'C003633\', \'C003636\', \'C003643\', \'C003649\', \'C003652\', \'C003653\', \'C003654\', \'C003655\', \'C003662\', \'C003663\', \'C003665\', \'C003670\', \'C003672\', \'C003676\', \'C003677\', \'C003679\', \'C003681\', \'C003683\', \'C003684\', \'C003687\', \'C003696\', \'C003698\', \'C003704\', \'C003708\', \'C003722\', \'C003723\', \'C003725\', \'C003727\', \'C003729\', \'C003730\', \'C003731\', \'C003734\', \'C003735\', \'C003736\', \'C003737\', \'C003738\', \'C003744\', \'C003745\', \'C003746\', \'C003747\', \'C003748\', \'C003749\', \'C003750\', \'C003751\', \'C003754\', \'C003755\', \'C003756\', \'C003757\', \'C003759\', \'C003765\', \'C003768\', \'C003770\', \'C003772\', \'C003773\', \'C003776\', \'C003779\', \'C003781\', \'C003784\', \'C003785\', \'C003787\', \'C003794\', \'C003798\', \'C003799\', \'C003803\', \'C003813\', \'C003815\', \'C003816\', \'C003817\', \'C003818\', \'C003819\', \'C003820\', \'C003821\', \'C003822\', \'C003824\', \'C003825\', \'C003828\', \'C003830\', \'C003831\', \'C003836\', \'C003848\', \'C003849\', \'C003853\', \'C003856\', \'C003857\', \'C003865\', \'C003873\', \'C003876\', \'C003878\', \'C003880\', \'C003882\', \'C003885\', \'C003886\', \'C003889\', \'C003890\', \'C003891\', \'C003894\', \'C003895\', \'C003898\', \'C003903\', \'C003908\', \'C003911\', \'C003912\', \'C003913\', \'C003914\', \'C003915\', \'C003918\', \'C003919\', \'C003923\', \'C003924\', \'C003925\', \'C003935\', \'C003937\', \'C003938\', \'C003939\', \'C003940\', \'C003942\', \'C003943\', \'C003944\', \'C003950\', \'C003956\', \'C003957\', \'C003959\', \'C003960\', \'C003961\', \'C003962\', \'C003963\', \'C003965\', \'C003968\', \'C003969\', \'C003970\', \'C003973\', \'C003975\', \'C003979\', \'C003984\', \'C003985\', \'C003989\', \'C003992\', \'C004002\', \'C004006\', \'C004013\', \'C004014\', \'C004017\', \'C004019\', \'C004020\', \'C004026\', \'C004035\', \'C004037\', \'C004041\', \'C004047\', \'C004050\', \'C004051\', \'C004052\', \'C004054\', \'C004055\', \'C004056\', \'C004059\', \'C004065\', \'C004066\', \'C004067\', \'C004068\', \'C004074\', \'C004076\', \'C004083\', \'C004085\', \'C004098\', \'C004100\', \'C004106\', \'C004110\', \'C004112\', \'C004115\', \'C004126\', \'C004127\', \'C004134\', \'C004140\', \'C004141\', \'C004147\', \'C004151\', \'C004153\', \'C004155\', \'C004162\', \'C004169\', \'C004170\', \'C004171\', \'C004179\', \'C004180\', \'C004181\', \'C004184\', \'C004186\', \'C004188\', \'C004191\', \'C004199\', \'C004201\', \'C004202\', \'C004203\', \'C004206\', \'C004207\', \'C004208\', \'C004210\', \'C004215\', \'C004217\', \'C004219\', \'C004223\', \'C004228\', \'C004229\', \'C004235\', \'C004238\', \'C004242\', \'C004243\', \'C004244\', \'C004248\', \'C004253\', \'C004254\', \'C004256\', \'C004258\', \'C004259\', \'C004260\', \'C004263\', \'C004266\', \'C004268\', \'C004269\', \'C004271\', \'C004272\', \'C004278\', \'C004288\', \'C004296\', \'C004299\', \'C004302\', \'C004312\', \'C004313\', \'C004317\', \'C004323\', \'C004324\', \'C004325\', \'C004327\', \'C004331\', \'C004334\', \'C004336\', \'C004337\', \'C004342\', \'C004344\', \'C004345\', \'C004347\', \'C004349\', \'C004505\', \'C004507\', \'C004508\', \'C004512\', \'C004513\', \'C004514\', \'C004517\', \'C004521\', \'C004524\', \'C004525\', \'C004526\', \'C004527\', \'C004530\', \'C004532\', \'C004533\', \'C004534\', \'C004535\', \'C004537\', \'C004543\', \'C004545\', \'C004550\', \'C004551\', \'C004552\', \'C004554\', \'C004555\', \'C004566\', \'C004567\', \'C004568\', \'C004570\', \'C004571\', \'C004573\', \'C004582\', \'C004583\', \'C004584\', \'C004586\', \'C004588\', \'C004589\', \'C004591\', \'C004594\', \'C004595\', \'C004599\', \'C004600\', \'C004601\', \'C004602\', \'C004609\', \'C004613\', \'C004617\', \'C004618\', \'C004620\', \'C004623\', \'C004624\', \'C004626\', \'C004629\', \'C004630\', \'C004635\', \'C004643\', \'C004646\', \'C004650\', \'C004652\', \'C004653\', \'C004654\', \'C004657\', \'C004664\', \'C004665\', \'C004666\', \'C004668\', \'C004671\', \'C004672\', \'C004673\', \'C004674\', \'C004675\', \'C004676\', \'C004679\', \'C004680\', \'C004681\', \'C004684\', \'C004688\', \'C004689\', \'C004691\', \'C004695\', \'C004696\', \'C004697\', \'C004698\', \'C004699\', \'C004701\', \'C004703\', \'C004707\', \'C004708\', \'C004711\', \'C004713\', \'C004714\', \'C004715\', \'C004726\', \'C004731\', \'C004736\', \'C004739\', \'C004741\', \'C004742\', \'C004746\', \'C004747\', \'C004749\', \'C004752\', \'C004755\', \'C004757\', \'C004758\', \'C004761\', \'C004770\', \'C004775\', \'C004776\', \'C004777\', \'C004778\', \'C004779\', \'C004782\', \'C004784\', \'C004787\', \'C004790\', \'C004791\', \'C004799\', \'C004800\', \'C004801\', \'C004803\', \'C004804\', \'C004809\', \'C004810\', \'C004812\', \'C004813\', \'C004816\', \'C004817\', \'C004824\', \'C004827\', \'C004828\', \'C004829\', \'C004830\', \'C004832\', \'C004834\', \'C004835\', \'C004838\', \'C004842\', \'C004851\', \'C004859\', \'C004862\', \'C004869\', \'C004873\', \'C004874\', \'C004875\', \'C004876\', \'C004877\', \'C004879\', \'C004880\', \'C004881\', \'C004882\', \'C004883\', \'C004884\', \'C004886\', \'C004888\', \'C004889\', \'C004891\', \'C004892\', \'C004893\', \'C004895\', \'C004896\', \'C004897\', \'C004899\', \'C004920\', \'C004921\', \'C004922\', \'C004923\', \'C004924\', \'C004925\', \'C004926\', \'C004927\', \'C004934\', \'C004936\', \'C004938\', \'C004941\', \'C004943\', \'C004944\', \'C004945\', \'C004948\', \'C004949\', \'C004950\', \'C004952\', \'C004954\', \'C004955\', \'C004956\', \'C004959\', \'C004960\', \'C004961\', \'C004964\', \'C004965\', \'C004966\', \'C004968\', \'C004969\', \'C004971\', \'C004972\', \'C004974\', \'C004975\', \'C004976\', \'C004980\', \'C004981\', \'C004982\', \'C004984\', \'C004986\', \'C004988\', \'C004990\', \'C004991\', \'C004992\', \'C004993\', \'C004995\', \'C004996\', \'C005000\', \'C005004\', \'C005006\', \'C005008\', \'C005011\', \'C005012\', \'C005014\', \'C005015\', \'C005017\', \'C005018\', \'C005019\', \'C005020\', \'C005021\', \'C005023\', \'C005024\', \'C005025\', \'C005026\', \'C005027\', \'C005030\', \'C005031\', \'C005032\', \'C005033\', \'C005036\', \'C005038\', \'C005042\', \'C005043\', \'C005044\', \'C005049\', \'C005051\', \'C005052\', \'C005058\', \'C005059\', \'C005061\', \'C005065\', \'C005067\', \'C005075\', \'C005087\', \'C005089\', \'C005090\', \'C005096\', \'C005098\', \'C005099\', \'C005102\', \'C005103\', \'C005112\', \'C005119\', \'C005121\', \'C005124\', \'C005126\', \'C005127\', \'C005129\', \'C005130\', \'C005131\', \'C005132\', \'C005135\', \'C005136\', \'C005137\', \'C005142\', \'C005145\', \'C005148\', \'C005150\', \'C005152\', \'C005154\', \'C005156\', \'C005157\', \'C005159\', \'C005167\', \'C005168\', \'C005170\', \'C005172\', \'C005178\', \'C005180\', \'C005185\', \'C005188\', \'C005189\', \'C005191\', \'C005192\', \'C005195\', \'C005196\', \'C005199\', \'C005202\', \'C005203\', \'C005204\', \'C005205\', \'C005207\', \'C005212\', \'C005214\', \'C005215\', \'C005219\', \'C005223\', \'C005224\', \'C005226\', \'C005227\', \'C005231\', \'C005232\', \'C005234\', \'C005235\', \'C005236\', \'C005237\', \'C005239\', \'C005242\', \'C005244\', \'C005251\', \'C005252\', \'C005253\', \'C005255\', \'C005256\', \'C005259\', \'C005260\', \'C005262\', \'C005264\', \'C005265\', \'C005269\', \'C005270\', \'C005271\', \'C005279\', \'C005281\', \'C005282\', \'C005283\', \'C005285\', \'C005287\', \'C005288\', \'C005290\', \'C005292\', \'C005294\', \'C005297\', \'C005301\', \'C005302\', \'C005303\', \'C005307\', \'C005310\', \'C005311\', \'C005312\', \'C005313\', \'C005319\', \'C005321\', \'C005322\', \'C005325\', \'C005326\', \'C005328\', \'C005329\', \'C005330\', \'C005331\', \'C005334\', \'C005336\', \'C005339\', \'C005340\', \'C005342\', \'C005343\', \'C005347\', \'C005348\', \'C005351\', \'C005352\', \'C005353\', \'C005355\', \'C005359\', \'C005361\', \'C005362\', \'C005365\', \'C005366\', \'C005375\', \'C005379\', \'C005380\', \'C005386\', \'C005388\', \'C005390\', \'C005392\', \'C005397\', \'C005398\', \'C005399\', \'C005402\', \'C005403\', \'C005404\', \'C005405\', \'C005406\', \'C005407\', \'C005408\', \'C005411\', \'C005412\', \'C005414\', \'C005415\', \'C005419\', \'C005425\', \'C005426\', \'C005427\', \'C005428\', \'C005429\', \'C005430\', \'C005431\', \'C005436\', \'C005439\', \'C005442\', \'C005445\', \'C005447\', \'C005449\', \'C005450\', \'C005452\', \'C005453\', \'C005454\', \'C005456\', \'C005460\', \'C005463\', \'C005467\', \'C005468\', \'C005469\', \'C005470\', \'C005474\', \'C005476\', \'C005479\', \'C005481\', \'C005482\', \'C005484\', \'C005485\', \'C005486\', \'C005489\', \'C005491\', \'C005492\', \'C005493\', \'C005494\', \'C005497\', \'C005499\', \'C006000\', \'C006001\', \'C006002\', \'C006003\', \'C006005\', \'C006006\', \'C006007\', \'C006010\', \'C006011\', \'C006013\', \'C006014\', \'C006015\', \'C006017\', \'C006018\', \'C006019\', \'C006021\', \'C006022\', \'C006023\', \'C006025\', \'C006026\', \'C006028\', \'C006029\', \'C006030\', \'C006032\', \'C006033\', \'C006034\', \'C006036\', \'C006037\', \'C006040\', \'C006041\', \'C006051\', \'C006052\', \'C006054\', \'C006056\', \'C006057\', \'C006062\', \'C006063\', \'C006067\', \'C006068\', \'C006070\', \'C006071\', \'C006073\', \'C006074\', \'C006077\', \'C006078\', \'C006079\', \'C006081\', \'C006084\', \'C006087\', \'C006090\', \'C006095\', \'C006097\', \'C006098\', \'C006102\', \'C006106\', \'C006112\', \'C006114\', \'C006115\', \'C006120\', \'C006121\', \'C006122\', \'C006123\', \'C006124\', \'C006126\', \'C006133\', \'C006134\', \'C006135\', \'C006136\', \'C006139\', \'C006142\', \'C006146\', \'C006149\', \'C006153\', \'C006156\', \'C006158\', \'C006159\', \'C006160\', \'C006162\', \'C006163\', \'C006164\', \'C006165\', \'C006166\', \'C006167\', \'C006174\', \'C006176\', \'C006178\', \'C006179\', \'C006182\', \'C006183\', \'C006184\', \'C006185\', \'C006188\', \'C006190\', \'C006192\', \'C006195\', \'C006196\', \'C006201\', \'C006202\', \'C006206\', \'C006207\', \'C006208\', \'C006209\', \'C006211\', \'C006214\', \'C006216\', \'C006217\', \'C006218\', \'C006219\', \'C006220\', \'C006222\', \'C006223\', \'C006225\', \'C006226\', \'C006227\', \'C006230\', \'C006231\', \'C006232\', \'C006235\', \'C006236\', \'C006237\', \'C006238\', \'C006240\', \'C006242\', \'C006244\', \'C006246\', \'C006247\', \'C006251\', \'C006253\', \'C006255\', \'C006257\', \'C006259\', \'C006260\', \'C006262\', \'C006263\', \'C006266\', \'C006270\', \'C006271\', \'C006272\', \'C006273\', \'C006278\', \'C006280\', \'C006281\', \'C006282\', \'C006285\', \'C006286\', \'C006288\', \'C006289\', \'C006291\', \'C006292\', \'C006293\', \'C006298\', \'C006302\', \'C006303\', \'C006308\', \'C006309\', \'C006313\', \'C006316\', \'C006318\', \'C006321\', \'C006323\', \'C006325\', \'C006327\', \'C006328\', \'C006332\', \'C006334\'"\n    # devices1="\'C011669\', \'C011563\', \'C011641\', \'C011747\', \'C011526\', \'C011685\', \'C011601\', \'C011564\', \'C011637\', \'C011741\', \'C011757\', \'C011710\', \'C011569\', \'C011698\', \'C011622\', \'C011731\', \'C011558\', \'C011192\', \'C011445\', \'C011692\', \'C011608\', \'C011723\', \'C011724\', \'C011606\', \'C011744\', \'C011607\', \'C011733\', \'C011728\', \'C011631 \', \'C011511\', \'C011700\', \'C011595\', \'C011725\', \'C010561\', \'C011152\', \'C010565\', \'C011145\', \'C010592\', \'C010621\'"\n    sql_query = query_template_raw.format(schema=\'dummy\', device=devices1, start=begin, end=end)\n\n    df = pd.read_sql_query(sql_query, cnx)\n\n    return df\n\ndf_health = read_health(pg_conn, "dummy", start, end)\ndf_health.to_parquet(f\'./data/oneK_health.parquet\')')


# # 2  Read in health and dsd data for 1K M2

def dsd_processing(dsd_df, df_health):
    '''
    clean dsd_sum file and merge with df_health dataframe
    '''
    dsd_df['time'] = dsd_df['five_minute_interval'].dt.floor('h')

    dsd_df=dsd_df[['time' , 'device' , 'droplet_counts']]

    dsd_df = dsd_df.groupby(['device', 'time']).agg({'droplet_counts': 'sum'}).reset_index()

    joint_df = pd.merge(dsd_df, df_health, on=['device', 'time'], how='inner')
    return joint_df


df_health = pd.read_parquet('./data/oneK_health.parquet')


df_health.columns = ['time', 'device', 'country', 'min_batt_volt']


dsd_df = pd.DataFrame()

for i in range(1, 12):
    temp = pd.read_parquet(f'../pull_calval_disdro_notebook/data/M2_dsd_1K_2022-{i}-01.parquet')
    dsd_df = pd.concat([dsd_df, temp])


joint_df = dsd_processing(dsd_df, df_health)

df_to_s3(joint_df, key='mark3_tbelow/oneK_M2_dsdsum_minVolt.parquet', bucket='arable-adse-dev', format="parquet")

joint_df.loc[joint_df.min_batt_volt > 0].plot(x='min_batt_volt', y='droplet_counts', kind='scatter')

# ### import LATM_dsd_sum and LATM health


LATAM_health = pd.read_csv('../pull_calval_disdro_notebook/data/hourly_latam_min_volt_hourly.csv')

LATAM_health.columns = ['time', 'device', 'region', 'country', 'min_batt_volt']

LATAM_health['time'] = pd.to_datetime(LATAM_health['time'], utc=True)


# In[28]:

dsd_LATM_df = pd.DataFrame()

for i in range(1, 12):
    temp = pd.read_parquet(f'../pull_calval_disdro_notebook/data/M2_dsd_LATM_2022-{i}-01.parquet')
    dsd_LATM_df = pd.concat([dsd_LATM_df, temp])


joint_LATAM = dsd_processing(dsd_LATM_df, LATAM_health)


joint_LATAM.columns = ['device', 'time', 'avg_dsd_sum', 'region', 'country', 'min_batt_volt']

df_to_s3(joint_LATAM, key='mark3_tbelow/LATAM_M2_dsdsum_minVolt.parquet', bucket='arable-adse-dev', format="parquet")

joint_LATAM.loc[joint_LATAM.min_batt_volt > 0].plot(x='min_batt_volt', y='avg_dsd_sum', kind='scatter')
