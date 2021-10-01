using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class mouseMove : MonoBehaviour
{
    public float sensitivityMouse = 2f;
    public float sensitivetyKeyBoard = 0.1f;
    public float sensitivetyMouseWheel = 10f;

    void Update()
    {
        if (Input.GetAxis("Mouse ScrollWheel") != 0)
        {
            this.GetComponent<Camera>().fieldOfView = this.GetComponent<Camera>().fieldOfView - Input.GetAxis("Mouse ScrollWheel") * sensitivetyMouseWheel;
        }
        if (Input.GetMouseButton(1))
        {
            transform.Rotate(-Input.GetAxis("Mouse Y") * sensitivityMouse, Input.GetAxis("Mouse X") * sensitivityMouse, 0);
        }
        if (Input.GetKey("q")) 
        {
            transform.Rotate(0, sensitivityMouse*0.5f, 0);
        }
        else if (Input.GetKey("e"))
        {
            transform.Rotate(0, -sensitivityMouse*0.5f, 0);
        }

        if (Input.GetAxis("Horizontal") != 0)
        {
            transform.Translate(Input.GetAxis("Horizontal") * sensitivetyKeyBoard, 0, 0);
        }
        if (Input.GetAxis("Vertical") != 0)
        {
            transform.Translate(0, Input.GetAxis("Vertical") * sensitivetyKeyBoard, 0);
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

    public void topView()
    {
        this.GetComponent<Camera>().fieldOfView = 60;
        transform.position = new Vector3(0, 0, 50);
        //transform.Rotate(0, 0, 0);
        //transform.rotation = CalQuaternion(new Vector3((float)0.0, (float)1.0, (float)0.0));
    }

    public void mainView()
    {
        this.GetComponent<Camera>().fieldOfView = 60;
        transform.position = new Vector3(0, -20, 50);

        //transform.rotation = CalQuaternion(new Vector3((float)0, (float)-1.0, (float)-1.0));
    }
    public void sideView()
    {
        this.GetComponent<Camera>().fieldOfView = 60;
        transform.position = new Vector3(-20, 0, 50);
        //transform.rotation = CalQuaternion(new Vector3((float)-1.0, (float)0.0, (float)-1.0));
    }
}
