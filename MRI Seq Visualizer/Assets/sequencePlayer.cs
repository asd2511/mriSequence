using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;
using Newtonsoft.Json.Linq;
using System.IO;
using System.Text;
using System;


public class sequencePlayer : MonoBehaviour
{
    public GameObject moment;
    public GameObject textTime;
    public GameObject textRep;
    public GameObject textEvent;
    public GameObject textAngle;
    public GameObject textPhase;
    public GameObject inputFPS;
    GameObject[,] spinMatrix;
    JObject data;

    List<double[,,]> posEvent = new List<double[,,]>();
    List<double[]> paramEvent = new List<double[]>();

    List<double[,,]> posInterpolate = new List<double[,,]>();
    List<double[]> paramInterpolate = new List<double[]>();
    // Start is called before the first frame update
    int idx = 0;
    int row = 0;
    int col = 0;

    void Start()
    {
        
    }

    public void reset()
    {
        //spinMatrix = new GameObject[row, col];
        idx = 0;
        for (int i = 0; i < row; i++)
        {
            for (int j = 0; j < col; j++)
            {
                Destroy(spinMatrix[i, j], (float)0.01);
            }
        }
    }

    public void load(GameObject inputFileName)
    {
        string json = File.ReadAllText(Application.dataPath + "\\StreamingAssets\\" + inputFileName.GetComponent<InputField>().text +".json", Encoding.UTF8);
        data = JObject.Parse(json);

        // for the spinMatix
        row = int.Parse(data["param"]["size"][0].ToString());
        col = int.Parse(data["param"]["size"][1].ToString());
        spinMatrix = new GameObject[row, col];
        reset();

        idx = 0;
        for (int i = 0; i < row; i++)
        {
            for (int j = 0; j < col; j++)
            {
                spinMatrix[i, j] = Instantiate(moment);
                spinMatrix[i, j].transform.position = new Vector3(i - row / 2, j - col / 2, 3);
            }
        }

        int NRep = 3; //int.Parse(data["param"]["#Rep"].ToString());
        int NEvent = int.Parse(data["param"]["#Event"].ToString());
        for (int r = 0; r < NRep; r++)
        {
            for (int t = 0; t < NEvent; t++)
            {
                JArray xJArray = JArray.Parse(data["spin"]["x"][r.ToString()][t.ToString()].ToString());
                JArray yJArray = JArray.Parse(data["spin"]["y"][r.ToString()][t.ToString()].ToString());
                JArray zJArray = JArray.Parse(data["spin"]["z"][r.ToString()][t.ToString()].ToString());
                double[ , ,] matrix = json2mat(xJArray, yJArray, zJArray);
                double time = double.Parse(data["spin"]["t"][r.ToString()][t.ToString()].ToString())*1000;
                JArray pJArray = JArray.Parse(data["sequence"]["flip"][r.ToString()][t.ToString()].ToString());
                double angle = double.Parse(pJArray[0].ToString());
                double phase = double.Parse(pJArray[1].ToString());
                posEvent.Add(matrix);
                paramEvent.Add(new double[] { time, r, t, angle, phase });
                //Debug.Log(time);
            }
        }
    }
    
    double[ , ,] json2mat(JArray xMatrix, JArray yMatrix, JArray zMatrix)
    {
        //row = xMatrix.Count;
        //col = JArray.Parse(xMatrix[0].ToString()).Count; 
        double[ , ,] matrix = new double[row, col, 3];
        for (int i = 0; i < row; i++)
        {
            JArray xArray = JArray.Parse(xMatrix[i].ToString());
            JArray yArray = JArray.Parse(yMatrix[i].ToString());
            JArray zArray = JArray.Parse(zMatrix[i].ToString());
            for (int j = 0; j < col; j++)
            {
                matrix[i, j, 0] = double.Parse(xArray[j].ToString());
                matrix[i, j, 1] = double.Parse(yArray[j].ToString());
                matrix[i, j, 2] = double.Parse(zArray[j].ToString());
            }
        }
        return matrix;
    }

    void setSpin(double[,,] data)
    {
        for (int r = 0; r < row; r++)
        {
            for (int c = 0; c < col; c++)
            {
                double x = data[r, c, 0];
                double y = data[r, c, 1];
                double z = data[r, c, 2];

                double radius = (double)Math.Sqrt(x * x + y * y + z * z);
                double h = (Math.Atan2(x, y) * 180 / 3.1415926 + 180) / 360;
                double s = Math.Sqrt(x * x + y * y);
                spinMatrix[r, c].GetComponent<Renderer>().material.color = Color.HSVToRGB((float)h, (float)s, (float)1.0);
                //spinMatrix[r, c].transform.Rotate((float)xRot, 0, (float)yRot, Space.World);
                spinMatrix[r, c].transform.rotation = CalQuaternion(new Vector3((float)x, (float)y, (float)z));
                spinMatrix[r, c].transform.localScale = new Vector3((float)0.25, (float)radius,(float)0.25);

            }
        }
    }
    
    public Quaternion CalQuaternion(Vector3 dir)
    {
        Quaternion cal = new Quaternion();
        Vector3 euler = Quaternion.LookRotation(dir).eulerAngles;

        float CosY = dir.z / Mathf.Sqrt(dir.x * dir.x + dir.z * dir.z);
        float CosYDiv2 = Mathf.Sqrt((CosY + 1) / 2);
        if (dir.x < 0) CosYDiv2 = -CosYDiv2;

        float SinYDiv2 = Mathf.Sqrt((1 - CosY) / 2);

        float CosX = Mathf.Sqrt((dir.x * dir.x + dir.z * dir.z) / (dir.x * dir.x + dir.y * dir.y + dir.z * dir.z));
        if (dir.z < 0) CosX = -CosX;
        float CosXDiv2 = Mathf.Sqrt((CosX + 1) / 2);
        if (dir.y > 0) CosXDiv2 = -CosXDiv2;
        float SinXDiv2 = Mathf.Sqrt((1 - CosX) / 2);

        cal.w = CosXDiv2 * CosYDiv2;
        cal.x = SinXDiv2 * CosYDiv2;
        cal.y = CosXDiv2 * SinYDiv2;
        cal.z = -SinXDiv2 * SinYDiv2;

        return cal;
    }
    

    public void nextEvent()
    {
        if (posEvent.Count != 0)
        {
            setSpin(posEvent[idx]);
            setTextVar( paramEvent[idx]);
            ++idx;
            if (idx >= posEvent.Count) { idx = 0; }
        }
    }

    public void prevEvent()
    {
        if (posEvent.Count != 0)
        {
            setSpin(posEvent[idx]);
            setTextVar(paramEvent[idx]);
            --idx;
            if (idx <= 0) { idx = posEvent.Count-1; }
        }
    }

    void setTextVar(double[] param)
    {
        textTime.GetComponent<Text>().text = param[0].ToString("f2");
        textRep.GetComponent<Text>().text = param[1].ToString("f2");
        textEvent.GetComponent<Text>().text = param[2].ToString("f2");
        textAngle.GetComponent<Text>().text = (param[3] * 180 / 3.14).ToString("f2");
        textPhase.GetComponent<Text>().text = (param[4] * 180 / 3.14).ToString("f2");
    }

    public void startInterpolated()
    {
        idx = 0;
        float fps = 1/float.Parse(inputFPS.GetComponent<InputField>().text);
        InvokeRepeating("nextEvent", 1.0f, fps);
    }
    
    public void pause()
    {
        CancelInvoke();
    }

}
