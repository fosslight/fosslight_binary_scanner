#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import tlsh
import logging
import psycopg2
import pandas as pd
from urllib.parse import urlparse
from ._binary import _TLSH_CHECKSUM_NULL, OssItem
import fosslight_util.constant as constant

columns = ['filename', 'pathname', 'checksum', 'tlshchecksum', 'ossname',
           'ossversion', 'license', 'platformname',
           'platformversion']
conn = ""
cur = ""
logger = logging.getLogger(constant.LOGGER_NAME)


def get_oss_info_from_db(bin_info_list, dburl=""):
    _cnt_auto_identified = 0
    conn_str = get_connection_string(dburl)
    connect_to_lge_bin_db(conn_str)

    if conn != "" and cur != "":
        for item in bin_info_list:
            bin_oss_items = []
            tlsh_value = item.tlsh
            checksum_value = item.checksum
            bin_file_name = item.binary_name_without_path

            df_result = get_oss_info_by_tlsh_and_filename(
                bin_file_name, checksum_value, tlsh_value)
            if df_result is not None and len(df_result) > 0:
                _cnt_auto_identified += 1
                for idx, row in df_result.iterrows():
                    oss_from_db = OssItem(
                        row['ossname'], row['ossversion'], row['license'])
                    oss_from_db.set_comment("Binary DB Result")
                    bin_oss_items.append(oss_from_db)

                if bin_oss_items:
                    item.found_in_db = True
                    item.set_oss_items(bin_oss_items, True, "Excluded due to Binary DB.")
    disconnect_lge_bin_db()
    return bin_info_list, _cnt_auto_identified


def get_connection_string(dburl):
    # dburl format : 'postgresql://username:password@host:port/database_name'
    connection_string = ""
    user_dburl = True
    if dburl == "" or dburl is None:
        user_dburl = False
        dburl = "postgresql://bin_analysis_script_user:script_123@bat.lge.com:5432/bat"
    try:
        if user_dburl:
            logger.debug("DB URL:" + dburl)
        dbc = urlparse(dburl)
        connection_string = "dbname={dbname} user={user} host={host} password={password} port={port}" \
            .format(dbname=dbc.path.lstrip('/'),
                    user=dbc.username,
                    host=dbc.hostname,
                    password=dbc.password,
                    port=dbc.port)
    except Exception as ex:
        if user_dburl:
            logger.warning(f"(Minor) Failed to parsing db url : {ex}")

    return connection_string


def get_oss_info_by_tlsh_and_filename(file_name, checksum_value, tlsh_value):
    sql_statement = "SELECT filename,pathname,checksum,tlshchecksum,ossname,ossversion,\
                    license,platformname,platformversion FROM lgematching "
    sql_statement_checksum = " WHERE filename='{fname}' AND checksum='{checksum}';".format(fname=file_name,
                                                                                           checksum=checksum_value)  # Checking checksum first.
    sql_statement_filename = "SELECT DISTINCT ON (tlshchecksum) tlshchecksum FROM lgematching WHERE filename='{fname}';".format(
        fname=file_name)  # For getting tlsh values of file.

    final_result_item = ""

    df_result = get_list_by_using_query(
        sql_statement + sql_statement_checksum, columns)
    # Found a file with the same checksum.
    if df_result is not None and len(df_result) > 0:
        final_result_item = df_result
    else:
        # Match tlsh and fileName
        df_result = get_list_by_using_query(
            sql_statement_filename, ['tlshchecksum'])
        if df_result is None or len(df_result) <= 0:
            final_result_item = ""
        elif tlsh_value == _TLSH_CHECKSUM_NULL:  # Couldn't get the tlsh of a file.
            final_result_item = ""
        else:
            matched_tlsh = ""
            matched_tlsh_diff = -1
            for row in df_result.tlshchecksum:
                try:
                    if row != _TLSH_CHECKSUM_NULL:
                        tlsh_diff = tlsh.diff(row, tlsh_value)
                        if tlsh_diff <= 120:  # MATCHED
                            if (matched_tlsh_diff < 0) or (tlsh_diff < matched_tlsh_diff):
                                matched_tlsh_diff = tlsh_diff
                                matched_tlsh = row
                except Exception as ex:
                    logger.warning(f"* (Minor) Error_tlsh_comparison: {ex}")
            if matched_tlsh != "":
                final_result_item = get_list_by_using_query(
                    sql_statement + " WHERE filename='{fname}' AND tlshchecksum='{tlsh}';".format(fname=file_name,
                                                                                                  tlsh=matched_tlsh),
                    columns)

    return final_result_item


def get_list_by_using_query(sql_query, columns):
    result_rows = ""  # DataFrame
    cur.execute(sql_query)
    rows = cur.fetchall()

    if rows is not None and len(rows) > 0:
        result_rows = pd.DataFrame(data=rows, columns=columns)
    return result_rows


def disconnect_lge_bin_db():
    global conn, cur
    try:
        cur.close()
        conn.close()
    except:
        pass


def connect_to_lge_bin_db(connection_string):
    global conn, cur

    try:
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()
    except Exception as ex:
        logger.debug(f"(Minor) Can't connect to Binary DB. : {ex}")
        conn = ""
        cur = ""
