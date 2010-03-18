package model;

import java.io.IOException;
import swing.CmnSwingFrame;

/**
 *
 * @author konne
 */
public class CmnModel {
    public String index = "cmn_index";
    public String db_user = "root";
    public String db_password = "";
    public boolean clear_index = false;
    public String[] sources;

    public boolean generate_md5 = true;
    public boolean generate_fingerprint = true;
    public boolean generate_filename_tags = true;
    public boolean generate_foldername_tags = true;
    public boolean obtain_puid = true;
    public boolean obtain_id3_tags = true;
    public boolean obtain_musicid_tags = true;
    public boolean obtain_musicbrainz_tags = true;

    public int similarity_level = 80;

    public String destination = "";
    public boolean create_library = true;
    public boolean create_merge_overview = true;
    public boolean create_unplayable_file_overview = true;
    public String naming_scheme = "%a/%r/%t-%n";

    static public void CreateDatabase(String index){

    }

    public void Execute() {
        try {
            String[] commands = new String[]{
                "cmnindexer",
                "-d",
                "-d"
            };
            Process child = Runtime.getRuntime().exec(commands);
        } catch (IOException e) {
        }
    }
}
