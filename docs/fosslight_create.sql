-- --------------------------------------------------------
-- 호스트:                          
-- 서버 버전:                        PostgreSQL 9.3.24 on x86_64-unknown-linux-gnu, compiled by gcc (Ubuntu 4.8.4-2ubuntu1~14.04.4) 4.8.4, 64-bit
-- 서버 OS:                        
-- HeidiSQL 버전:                  10.2.0.5599
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES  */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
-- bat 데이터베이스 구조 내보내기
CREATE DATABASE IF NOT EXISTS `bat` DEFAULT CHARACTER SET utf8mb4;
CREATE USER 'bin_analysis_script_user'@'%' IDENTIFIED BY 'script_123';
CREATE USER 'bin_analysis_script_user'@'localhost' IDENTIFIED BY 'script_123';
GRANT ALL PRIVILEGES ON bat.* TO 'bin_analysis_script_user'@'%';
GRANT ALL PRIVILEGES ON bat.* TO 'bin_analysis_script_user'@'localhost';
FLUSH PRIVILEGES;

USE `bat`;

-- 테이블 public.lgematching 구조 내보내기
CREATE TABLE IF NOT EXISTS "lgematching" (
	"filename" TEXT NULL DEFAULT NULL COMMENT E'',
	"pathname" TEXT NULL DEFAULT NULL COMMENT E'',
	"checksum" TEXT NULL DEFAULT NULL COMMENT E'',
	"tlshchecksum" TEXT NULL DEFAULT NULL COMMENT E'',
	"ossname" TEXT NULL DEFAULT NULL COMMENT E'',
	"ossversion" TEXT NULL DEFAULT NULL COMMENT E'',
	"license" TEXT NULL DEFAULT NULL COMMENT E'',
	"parentname" TEXT NULL DEFAULT NULL COMMENT E'',
	"platformname" CHARACTER VARYING(100) NULL DEFAULT NULL::character varying COMMENT E'',
	"platformversion" CHARACTER VARYING(100) NULL DEFAULT NULL::character varying COMMENT E'',
	"updatedate" TIMESTAMP WITHOUT TIME ZONE NULL DEFAULT NULL COMMENT E'',
	"sourcepath" TEXT NULL DEFAULT NULL COMMENT E'',
	KEY ("filename"),
	KEY ("checksum")
);

-- 테이블 데이터 public.lgematching:506,495 rows 내보내기
/*!40000 ALTER TABLE "lgematching" DISABLE KEYS */;
INSERT INTO "lgematching" ("filename", "pathname", "checksum", "tlshchecksum", "ossname", "ossversion", "license", "parentname", "platformname", "platformversion", "updatedate", "sourcepath") VALUES
	(E'askalono.exe', E'third_party/askalono/askalono.exe', E'3f5c6bbf06ddf53a46634bb21691ab0757f3b80c', E'T138267C12BB86A9EDC06AC470878646225B31B4CA0B25BFFF41C455743E6AAF45F3D39C', E'askalono', E'', E'Apache-2.0', E'[123]windows app project', E'windows', E'10', E'2021-02-19 17:21:52.430065', E'third_party/src/askalono'),
	(E'askalono_macos', E'third_party/askalono/askalono_macos', E'b4856c381954151781c3a46739deccc2fb0e4f49', E'T117469D27F652686CE257C0701BDE57A26731F8350231AB6F37D4A6356E27DA09B8C383', E'askalono', E'', E'Apache-2.0', E'[1234]macOS app project', E'macOS', E'catalina', E'2021-01-08 09:13:16.718569', E'third_party/src/askalono');

/*!40000 ALTER TABLE "lgematching" ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
