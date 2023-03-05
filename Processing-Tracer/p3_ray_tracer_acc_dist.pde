// This is the starter code for the CS 6491 Ray Tracing project. //<>//
//
// The most important part of this code is the interpreter, which will
// help you parse the scene description (.cli) files.

Scene scene = new Scene();
Camera cam = new Camera(0, 300, 300);

Shader shader = new Shader();
MatrixStack mstack = new MatrixStack();
NamedObject namedObjects = new NamedObject();

WindingOrder WO = WindingOrder.CW;
BVH bvh = null;
String scenePosfix = "a";

boolean useBVH = false;
boolean debug_flag = false;

void setup() {
  size (300, 300);
  noStroke();
  background (0, 0, 0);
  scene.screen_w = 300;
  scene.screen_h = 300;
}

void keyPressed() {
  reset_scene();
  
  switch(key) {
    case '1':
      println(scenePosfix);
      interpreter("s01" + scenePosfix + ".cli");
      break;
    case '2':
      interpreter("s02" + scenePosfix + ".cli");
      break;
    case '3':
      interpreter("s03" + scenePosfix + ".cli");
      break;
    case '4':
      interpreter("s04" + scenePosfix + ".cli");
      break;
    case '5':
      interpreter("s05" + scenePosfix + ".cli");
      break;
    case '6':
      interpreter("s06" + scenePosfix + ".cli");
      break;
     case '7':
      interpreter("s07" + scenePosfix + ".cli");
      break;
    case '8':
      interpreter("s08" + scenePosfix + ".cli");
      break;
    case '9':
      interpreter("s09" + scenePosfix + ".cli");
      break;
    case '0':
      interpreter("s10" + scenePosfix + ".cli");
      break;
    case 'a':
      interpreter("s11" + scenePosfix + ".cli");
      break;
    case CODED:
      if (keyCode == SHIFT) {
        println("Shift!");
        scenePosfix = scenePosfix.equals("a") ? "b" : "a";
      }
      break;
  }
}

// this routine helps parse the text in a scene description file
void interpreter(String file) {
  println("Parsing '" + file + "'");
  String str[] = loadStrings (file);
  if (str == null) println ("Error! Failed to read the file.");
  
  Triangle tri = null;
  BBox box = null;
  Material material = null;
  
  for (int i = 0; i < str.length; i++) {
    String[] token = splitTokens (str[i], " ");   // get a line and separate the tokens
    if (token.length == 0) continue;              // skip blank lines

    if (token[0].equals("fov")) {
      float fov = float(token[1]);
      println("fov: " + fov);
      scene.camera.setFOV(fov);
      println("eye: ", scene.camera.eye);
      
    } else if (token[0].equals("background")) {
      // this is how to get a float value from a line in the scene description file
      float r = float(token[1]);  
      float g = float(token[2]);
      float b = float(token[3]);
      scene.bkColor = new Color(r, g, b);
      int r255 = int(255 * r);
      int g255 = int(255 * g);
      int b255 = int(255 * b);
      println ("background = " + r255 + " " + g255 + " " + b255);
      background(r255, g255, b255);
      
    } else if (token[0].equals("light")) {
      float r = float(token[4]);
      float g = float(token[5]);
      float b = float(token[6]);
      Color c = new Color(r, g, b);
      
      float x = float(token[1]);
      float y = float(token[2]);
      float z = float(token[3]);
      DirectionalLight light = new DirectionalLight(x, y, z, c, lightID);
      lightID++;
      scene.addLight(light);
      println ("directional light = ", light.x, light.y, light.z, c);
      
    } else if (token[0].equals("surface")) {
      float r = float(token[1]);
      float g = float(token[2]);
      float b = float(token[3]);
      Color diffuse = new Color(r, g, b);
      material = new Material(MaterialType.DIFFUSE, diffuse, null, 
                              -1, -1, -1);
    } else if (token[0].equals("begin")) {
      tri = new Triangle(material);
      tri.id = objectID;
      objectID++;
    } else if (token[0].equals("vertex")) {
      Point v = new Point(float(token[1]), float(token[2]), 
                          float(token[3]));
      v = mstack.transform(v);
      //println("tranformed point:", v);
      if (tri != null) {
        tri.setVertex(v);
      }
      
    } else if (token[0].equals("end")) {
      if (tri != null) {
        tri.setMaterial(material);
      }
      
      if (bvh != null) {
        bvh.addTriangle(tri);
      } else {
        scene.objects.add(tri);
      }
      tri = null;
      
    } else if (token[0].equals("render")) {
      draw_scene();   // this is where you actually perform the scene rendering
      
    } else if (token[0].equals("#")) {
      // comment (ignore)
      
    } else if (token[0].equals("read")) {
      if (WOList.contains(token[1])){
         WO = WindingOrder.CW;
      } else {
         WO = WindingOrder.CCW;
      }
      interpreter (token[1]);
      
    } else if (token[0].equals("push")) {
      mstack.pushLayer();
      
    } else if (token[0].equals("pop")) {
      mstack.popLayer();
      
    } else if (token[0].equals("translate")) {
      Matrix T = translateMT(float(token[1]), float(token[2]), 
                             float(token[3]));
      mstack.addToLayer(T);
      
    } else if (token[0].equals("rotate")) {
      if (token[2].equals("1")) {
        Matrix T = rotateXMT(float(token[1]));
        mstack.addToLayer(T);
      } else if (token[3].equals("1")) {
        Matrix T = rotateYMT(float(token[1]));
        mstack.addToLayer(T);
      } else if (token[4].equals("1")) {
        Matrix T = rotateZMT(float(token[1]));
        mstack.addToLayer(T);
      }
      
    } else if (token[0].equals("scale")) {
      Matrix T = scaleMT(float(token[1]), float(token[2]), 
                         float(token[3]));
      mstack.addToLayer(T);
      
    } else if (token[0].equals("box")) {
      float minx = float(token[1]); 
      float miny = float(token[2]); 
      float minz = float(token[3]);
      float maxx = float(token[4]); 
      float maxy = float(token[5]); 
      float maxz = float(token[6]);
    
      Point pmin = new Point(minx, miny, minz);
      Point pmax = new Point(maxx, maxy, maxz);
      pmin = mstack.transform(pmin);
      pmax = mstack.transform(pmax);
      
      float[] min3 = new float[]{pmin.x, pmin.y, pmin.z};
      float[] max3 = new float[]{pmax.x, pmax.y, pmax.z};
      box = new BBox(material, min3, max3, true);
      box.id = objectID;
      objectID++;
      scene.objects.add(box);
      
    } else if (token[0].equals("named_object")) {
      namedObjects.map.put(token[1], scene.getLastObject());
      scene.removeLastObject();
      
    } else if (token[0].equals("instance")) {
      SceneObject so = namedObjects.map.get(token[1]);
      ArrayList<Matrix> C = mstack.peek();
      Instance inst = new Instance(C, so);
      inst.id = objectID;
      objectID++;
      scene.objects.add(inst);
      
    } else if (token[0].equals("begin_accel")) {
      bvh = new BVH(1);
      useBVH = true;
      
    } else if (token[0].equals("end_accel")) {
      if (bvh != null) {
        println("BVH Tree Build Time:");
        reset_timer();
        bvh.build();
        print_timer();
        scene.objects.add(bvh);
        bvh = null;
      }
      
    } else if (token[0].equals("sphere")) {
       Point center = new Point(float(token[2]), 
                                float(token[3]), 
                                float(token[4]));
       center = mstack.transform(center);                       
       Sphere sphere = new Sphere(center, float(token[1])); 
       sphere.setMaterial(material);
       sphere.id = objectID;
       objectID++;
       scene.objects.add(sphere);
       
    } else if (token[0].equals("rays_per_pixel")) {
      spp = int(token[1]);
      scene.camera.setSPP(spp);
      
    } else if (token[0].equals("moving_object")) {
      SceneObject obj = scene.getLastObject();
      obj.useMotionBlur(float(token[1]), float(token[2]), 
                        float(token[3]));
      
    } else if (token[0].equals("disk_light")) {
      float r = float(token[8]);
      float g = float(token[9]);
      float b = float(token[10]);
      Color c = new Color(r, g, b);
      float radius = float(token[4]);
      
      float nx = float(token[5]);
      float ny = float(token[6]);
      float nz = float(token[7]);
      PVector normal = new PVector(nx, ny, nz);
      
      float x = float(token[1]);
      float y = float(token[2]);
      float z = float(token[3]);
      Point center = new Point(x, y, z);
      
      SpotLight light = new SpotLight(center, normal, radius, c, lightID);
      lightID++;
      scene.addLight(light);
      println ("spot light = ", center.x, center.y, center.z, c);
      
    } else if (token[0].equals("lens")) {
      Lens lens = new Lens(float(token[1]), float(token[2]));
      scene.camera.useLens(lens);
      
    } else if (token[0].equals("glossy")) {
      Color d = new Color(float(token[1]), float(token[2]), 
                          float(token[3]));
      Color s = new Color(float(token[4]), float(token[5]), 
                          float(token[6]));
      material = new Material(MaterialType.GLOSSY, d, s, 
                                       float(token[7]),
                                       float(token[8]),
                                       float(token[9]));
    } else if (token[0].equals("rotatex")) {
      Matrix T = rotateXMT(float(token[1]));
      mstack.addToLayer(T);
    } else if (token[0].equals("rotatey")) {
      Matrix T = rotateYMT(float(token[1]));
      mstack.addToLayer(T);
    } else if (token[0].equals("rotatez")) {
      Matrix T = rotateZMT(float(token[1]));
      mstack.addToLayer(T);
    }else {
      println ("unknown command: " + token[0]);
    }
  }
}

void reset_scene() {
  // reset your scene variables here
  WO = WindingOrder.CW;
  mstack = new MatrixStack();
  scene = new Scene();
  scene.screen_w = 300;
  scene.screen_h = 300;
  cam = new Camera(0, 300, 300);
  scene.camera = cam;
  noStroke();
  background (0, 0, 0);
}

// This is where you should put your code for creating eye rays and tracing them.
void draw_scene() {
  reset_timer();
  
  for (int y = 0; y < height; y++) {
    for (int x = 0; x < width; x++) {

      // Maybe set debug flag true for ONE pixel.
      // Have your routines (like ray/triangle intersection)
      // print information when this flag is set.
      debug_flag = false;
      if (x == 179 && y == 124)
        debug_flag = true;

      Color c = new Color(0, 0, 0);
      
      // create and cast an eye ray
      for (int i = 0; i < scene.camera.spp; ++i) {
        float randx = x + random(0, 1);
        float randy = scene.screen_h - y + random(0, 1);
        
        if (scene.camera.spp == 1) {
          randx = x + 0.5;
          randy = scene.screen_h - y + 0.5;
        }
        Ray ray = scene.camera.generateRay(randx, randy);
        
        // cast the current ray
        c = colorAdd(c, shader.getGlobalIllumination(ray, 1));
      }
      float r = c.r / scene.camera.spp;
      float g = c.g / scene.camera.spp;
      float b = c.b / scene.camera.spp;
      c = new Color(r, g, b);
      
      // make a tiny rectangle to fill the pixel
      set (x, y, color2Color(c));
    }
  }
  if (useBVH) {
    println("Scene Rendering Time via BVH:");
  }
  
  print_timer();
}

// prints mouse location clicks, for help debugging
void mousePressed() {
  println ("You pressed the mouse at " + mouseX + " " + mouseY);
}

// you don't need to add anything here
void draw() {
}
