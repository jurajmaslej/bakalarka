package com.example.jurko.qrreader2;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import java.lang.Math;

/**
 * Created by Jurko on 12. 2. 2016.
 */
public class Hash {
    String Qr;
    Long savedMobileTime;



    public Hash(String qr, Long savedMtime ){
        this.Qr = qr;
        this.savedMobileTime = savedMtime;

    }
    public String get_SHA_512_SecurePassword(String passwordToHash)
    {
        String generatedPassword = null;
        try {

            MessageDigest md = MessageDigest.getInstance("SHA-512");

            byte[] bytes = new byte[0];

                bytes = md.digest(passwordToHash.getBytes(java.nio.charset.Charset.forName("UTF-8")));

            StringBuilder sb = new StringBuilder();
            for(int i=0; i< bytes.length ;i++)
            {
                sb.append(Integer.toString((bytes[i] & 0xff) + 0x100, 16).substring(1));
            }
            generatedPassword = sb.toString();
        }
        catch (NoSuchAlgorithmException e)
        {
            e.printStackTrace();
        }
        return generatedPassword;
    }



    /*
    public String getTime (int acc){
        Long milis = System.currentTimeMillis();


        double milisDoub = (double) milis /  acc;
        Log.d("milis", "bf round > "+ milisDoub );
        int milisInt =  (int) Math.round( milisDoub);
        String time =  Integer.toString(milisInt);
        Log.d("milis", time);
        return time;
    }
    */

    public long roundSystemTime(){ // aby mal cas 10 cifier vsade, sekundova presnost, zaokruhli sa neskor
        return System.currentTimeMillis() / 1000;
    }


}
