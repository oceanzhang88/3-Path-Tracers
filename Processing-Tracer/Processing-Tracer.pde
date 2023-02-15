// This is the starter code for the CS 6491 Ray Tracing project. //<>// //<>//
//
// The most important part of this code is the interpreter, which will
// help you parse the scene description (.cli) files.

Scene scene = new Scene();
Shader shader = new Shader();
MatrixStack mstack = new MatrixStack();
NamedObject namedObjects = new NamedObject();

WindingOrder WO = WindingOrder.CCW;
BVH bvh = null;
Color diffuse = null;
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
      interpreter("s01.cli");
      break;
    case '2':
      interpreter("s02.cli");
      break;
    case '3':
      interpreter("s03.cli");
      break;
    case '4':
      WO = WindingOrder.CW;
      interpreter("s04.cli");
      break;
    case '5':
      WO = WindingOrder.CW;
      interpreter("s05.cli");
      break;
    case '6':
      interpreter("s06.cli");
      break;
     case '7':
      interpreter("s07.cli");
      break;
    case '8':
      interpreter("s08.cli");
      break;
    case '9':
      interpreter("s09.cli");
      break;
    case '0':
      
      interpreter("s10.cli");
      break;
    case 'a':
      interpreter("s11.cli");
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
  
  for (int i = 0; i < str.length; i++) {
    String[] token = splitTokens (str[i], " ");   // get a line and separate the tokens
    if (token.length == 0) continue;              // skip blank lines

    if (token[0].equals("fov")) {
      float fov = float(token[1]);
      println("fov: " + fov);
      Camera cam = new Camera(fov, 300, 300);
      scene.camera = cam;
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
      Light light = new Light(x, y, z, c, lightID);
      lightID++;
      scene.addLight(light);
      println ("light = ", light.x, light.y, light.z, c);
    } else if (token[0].equals("surface")) {
      float r = float(token[1]);
      float g = float(token[2]);
      float b = float(token[3]);
      diffuse = new Color(r, g, b);
    } else if (token[0].equals("begin")) {
      tri = new Triangle(diffuse);
    } else if (token[0].equals("vertex")) {
      Point v = new Point(float(token[1]), float(token[2]), float(token[3]));
      v = mstack.transform(v);
      //println("tranformed point:", v);
      if (tri != null) {
        tri.setVertex(v);
      }
    } else if (token[0].equals("end")) {
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
      // println("Skip #");
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
      Matrix T = translateMT(float(token[1]), float(token[2]), float(token[3]));
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
      Matrix T = scaleMT(float(token[1]), float(token[2]), float(token[3]));
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
      box = new BBox(diffuse, min3, max3, true);
      scene.objects.add(box);
    } else if (token[0].equals("named_object")) {
      namedObjects.map.put(token[1], scene.getLastObject());
      scene.removeLastObject();
    } else if (token[0].equals("instance")) {
      SceneObject so = namedObjects.map.get(token[1]);
      ArrayList<Matrix> C = mstack.peek();
      Instance inst = new Instance(C, so);
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
    } else {
      println ("unknown command: " + token[0]);
    }
  }
}

void reset_scene() {
  // reset your scene variables here
  WO = WindingOrder.CCW;
  mstack = new MatrixStack();
  scene = new Scene();
  scene.screen_w = 300;
  scene.screen_h = 300;
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
      if (x == 128 && y == 138)
        debug_flag = true;

      color c = color2Color(scene.bkColor);
      // create and cast an eye ray
      Ray ray = scene.camera.generateRay(x, scene.screen_h - y);
      // cast the current ray
      Hit hit = scene.castRay(ray);
      if (hit != null) {
        // set the pixel color, you should put the correct pixel color here
        c = shader.getDiffuseColor(scene.lights, hit);
      }
      // make a tiny rectangle to fill the pixel
      set (x, y, c);
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
