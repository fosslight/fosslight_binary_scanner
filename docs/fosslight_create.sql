--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;

SET default_tablespace = '';

SET default_with_oids = false;


--
-- Name: lgematching; Type: TABLE; Schema: public; Owner: bat; Tablespace:
--

CREATE TABLE public.lgematching (
    filename text,
    pathname text,
    checksum text,
    tlshchecksum text,
    ossname text,
    ossversion text,
    license text,
    parentname text,
    platformname character varying(100) DEFAULT NULL::character varying,
    platformversion character varying(100) DEFAULT NULL::character varying,
    updatedate timestamp without time zone,
    sourcepath text,
    UNIQUE (filename, checksum)
);


--
-- Data for Name: lgematching; Type: TABLE DATA; Schema: public; Owner: bat
--

INSERT INTO public.lgematching (filename, pathname, checksum, tlshchecksum, ossname, ossversion, license, parentname, platformname, platformversion, updatedate, sourcepath) VALUES
        ('askalono.exe', 'third_party/askalono/askalono.exe', '3f5c6bbf06ddf53a46634bb21691ab0757f3b80c', 'T138267C12BB86A9EDC06AC470878646225B31B4CA0B25BFFF41C455743E6AAF45F3D39C', 'askalono', '', 'Apache-2.0', '[123]windows app project', 'windows', '10', '2021-02-19 17:21:52.430065', 'third_party/src/askalono'),
        ('askalono_macos', 'third_party/askalono/askalono_macos', 'b4856c381954151781c3a46739deccc2fb0e4f49', 'T117469D27F652686CE257C0701BDE57A26731F8350231AB6F37D4A6356E27DA09B8C383', 'askalono', '', 'Apache-2.0', '[1234]macOS app project', 'macOS', 'catalina', '2021-01-08 09:13:16.718569', 'third_party/src/askalono');


GRANT ALL PRIVILEGES ON public.lgematching TO bin_analysis_script_user;

