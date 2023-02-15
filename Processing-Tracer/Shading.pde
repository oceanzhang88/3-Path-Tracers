class Light {
  float x;
  float y;
  float z;
  
  Color diffuseColor;
  int id;

  Light(float x, float y, float z, Color c, int id) {
    this.x = x;
    this.y = y;
    this.z = z;

    diffuseColor = c;
    this.id = id;
  }
}

class Color {
  public float r;
  public float g;
  public float b;

  Color(float r, float g, float b) {
    this.r = r;
    this.g = g;
    this.b = b;
  }

  @Override
    public String toString() {
    return "color: " + this.r + " " + this.g + " " + this.b;
  }
}

class Shader {
  public color getDiffuseColor(ArrayList<Light> lights, Hit hit) {
    int i = 0;
    Point p = hit.p;
    Color out = new Color(0, 0, 0);
    //if (debug_flag) {
    //      println("debug ray occuluded from light:", i);
    //}
    for(Light light : lights) {
      i++;
      if (scene.isOcculuded(hit, light)) {
        continue;
      }
      
      PVector normal = hit.normal;
      Color objDiffuse = hit.diffuse;
      Color lightDiffuse = light.diffuseColor;
      PVector l = new PVector(light.x - p.x, light.y - p.y, light.z - p.z);
      l.normalize();
      float ndotl = Math.max(0, normal.dot(l));
     
      Color albedo = colorBlend(objDiffuse, lightDiffuse);
      Color diffuse = colorMul(albedo, ndotl);
      out = colorAdd(out, diffuse);
    }
    return color2Color(out);
  }
}
