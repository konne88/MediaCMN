package model;

import java.io.IOException;

import java.beans.XMLEncoder;
import java.beans.XMLDecoder;
import java.io.*;

public class CmnModel {
    public boolean isClearIndex() {
        return clearIndex;
    }

    public boolean isCreateLibrary() {
        return createLibrary;
    }

    public boolean isCreateMergeOverview() {
        return createMergeOverview;
    }

    public boolean isCreateUnplayableFileOverview() {
        return createUnplayableFileOverview;
    }

    public String getDbPassword() {
        return dbPassword;
    }

    public String getDbUser() {
        return dbUser;
    }

    public String getDestination() {
        return destination;
    }

    public boolean isGenerateFilenameTags() {
        return generateFilenameTags;
    }

    public boolean isGenerateFingerprint() {
        return generateFingerprint;
    }

    public boolean isGenerateFoldernameTags() {
        return generateFoldernameTags;
    }

    public boolean isGenerateMd5() {
        return generateMd5;
    }

    public String getIndex() {
        return index;
    }

    public String getNamingScheme() {
        return namingScheme;
    }

    public boolean isObtainId3Tags() {
        return obtainId3Tags;
    }

    public boolean isObtainMusicbrainzTags() {
        return obtainMusicbrainzTags;
    }

    public boolean isObtainMusicidTags() {
        return obtainMusicidTags;
    }

    public boolean isObtainPuid() {
        return obtainPuid;
    }

    public int getSimilarityLevel() {
        return similarityLevel;
    }

    public String[] getSources() {
        return sources;
    }

    public void setClearIndex(boolean clearIndex) {
        this.clearIndex = clearIndex;
    }

    public void setCreateLibrary(boolean createLibrary) {
        this.createLibrary = createLibrary;
    }

    public void setCreateMergeOverview(boolean createMergeOverview) {
        this.createMergeOverview = createMergeOverview;
    }

    public void setCreateUnplayableFileOverview(boolean createUnplayableFileOverview) {
        this.createUnplayableFileOverview = createUnplayableFileOverview;
    }

    public void setDbPassword(String dbPassword) {
        this.dbPassword = dbPassword;
    }

    public void setDbUser(String dbUser) {
        this.dbUser = dbUser;
    }

    public void setDestination(String destination) {
        this.destination = destination;
    }

    public void setGenerateFilenameTags(boolean generateFilenameTags) {
        this.generateFilenameTags = generateFilenameTags;
    }

    public void setGenerateFingerprint(boolean generateFingerprint) {
        this.generateFingerprint = generateFingerprint;
    }

    public void setGenerateFoldernameTags(boolean generateFoldernameTags) {
        this.generateFoldernameTags = generateFoldernameTags;
    }

    public void setGenerateMd5(boolean generateMd5) {
        this.generateMd5 = generateMd5;
    }

    public void setIndex(String index) {
        this.index = index;
    }

    public void setNamingScheme(String namingScheme) {
        this.namingScheme = namingScheme;
    }

    public void setObtainId3Tags(boolean obtainId3Tags) {
        this.obtainId3Tags = obtainId3Tags;
    }

    public void setObtainMusicbrainzTags(boolean obtainMusicbrainzTags) {
        this.obtainMusicbrainzTags = obtainMusicbrainzTags;
    }

    public void setObtainMusicidTags(boolean obtainMusicidTags) {
        this.obtainMusicidTags = obtainMusicidTags;
    }

    public void setObtainPuid(boolean obtainPuid) {
        this.obtainPuid = obtainPuid;
    }

    public void setSimilarityLevel(int similarityLevel) {
        this.similarityLevel = similarityLevel;
    }

    public void setSources(String[] sources) {
        this.sources = sources;
    }

    private String destination = "";
    private boolean createLibrary = true;
    private boolean createMergeOverview = true;
    private boolean createUnplayableFileOverview = true;

    private String namingScheme = "%a/%r/%t-%n";
    private String index = "cmn_index";
    private String dbUser = "root";
    private String dbPassword = "";
    private boolean clearIndex = false;
    private String[] sources;

    private boolean generateMd5 = true;
    private boolean generateFingerprint = true;
    private boolean generateFilenameTags = true;
    private boolean generateFoldernameTags = true;
    private boolean obtainPuid = true;
    private boolean obtainId3Tags = true;
    private boolean obtainMusicidTags = true;
    private boolean obtainMusicbrainzTags = true;

    private int similarityLevel = 80;

    public void writeXml() throws FileNotFoundException {
        XMLEncoder encoder =
           new XMLEncoder(
              new BufferedOutputStream(
                new FileOutputStream(storePath)));
        encoder.writeObject(this);
        encoder.close();
    }

    static public CmnModel readXml(String filename) throws FileNotFoundException {
        XMLDecoder decoder =
            new XMLDecoder(new BufferedInputStream(
                new FileInputStream(filename)));
        CmnModel o = (CmnModel)decoder.readObject();
        o.storePath = filename;
        decoder.close();
        return o;
    }

    private String storePath = "";

    static public void CreateDatabase(String index){

    }

    public CmnModel(){}

    public CmnModel(String path){
        storePath = path;
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
