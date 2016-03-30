package com.example.jurko.qrreader2;
import android.util.Log;

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import java.lang.Math;

/**
 * Created by Jurko on 12. 2. 2016.
 */
public class Hash {


    public Hash( ){

    }
    public String get_SHA_512_SecurePassword(String passwordToHash, String   salt)
    {
        String generatedPassword = null;
        try {

            MessageDigest md = MessageDigest.getInstance("SHA-512");
            try {
                md.update(salt.getBytes("UTF-8"));
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
            byte[] bytes = new byte[0];
            try {
                bytes = md.digest(passwordToHash.getBytes("UTF-8"));
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
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

    public String getTime (int acc){
        Long milis = System.currentTimeMillis();


        double milisDoub = (double) milis /  acc;
        Log.d("milis", "bf round > "+ milisDoub );
        int milisInt =  (int) Math.round( milisDoub);
        String time =  Integer.toString(milisInt);
        Log.d("milis", time);
        return time;
    }
}