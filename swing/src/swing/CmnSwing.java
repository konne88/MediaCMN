    package swing;

import java.io.FileNotFoundException;
import javax.swing.UIManager;
import javax.swing.UnsupportedLookAndFeelException;
import model.CmnModel;

/**
 *
 * @author konne
 */
public class CmnSwing {
    public static void main(String args[]) {
        final String path = "/home/konne/Desktop/settings.xml";
        CmnModel tempModel;
        try {
            tempModel = CmnModel.readXml(path);
        } catch (FileNotFoundException ex) {
            tempModel = new CmnModel(path);
        }

        final CmnModel model = tempModel;
            //bmodel.setStorePath(path);
        try {
            // Set cross-platform Java L&F (also called "Metal")
            UIManager.setLookAndFeel(
                    //"com.seaglasslookandfeel.SeaGlassLookAndFeel");
                    UIManager.getSystemLookAndFeelClassName());
        } catch (UnsupportedLookAndFeelException e) {
            // handle exception
        } catch (ClassNotFoundException e) {
            // handle exception
        } catch (InstantiationException e) {
            // handle exception
        } catch (IllegalAccessException e) {
            // handle exception
        }

        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                new CmnSwingFrame(model).setVisible(true);
            }
        });
    }
}
